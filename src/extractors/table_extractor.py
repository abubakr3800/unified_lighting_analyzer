"""
Advanced Table Extraction with Quality Analysis
Based on the hybrid approach from gpt/extractor.py with enhancements
"""
import os
import re
import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime

# Core libraries
import numpy as np
import pandas as pd

# PDF processing
import pdfplumber
import fitz  # PyMuPDF

# Table extraction
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

# OCR and image processing
try:
    import cv2
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from ..core.config import config
except ImportError:
    from core.config import config

logger = logging.getLogger(__name__)

@dataclass
class TableQualityMetrics:
    """Quality metrics for extracted tables"""
    fill_ratio: float
    shape_score: float
    content_score: float
    structure_score: float
    noise_penalty: float
    overall_score: float
    confidence_level: str

@dataclass
class ExtractedTable:
    """Enhanced table extraction result"""
    dataframe: pd.DataFrame
    source_method: str
    page_number: int
    table_index: int
    quality_metrics: TableQualityMetrics
    headers: List[str]
    data_types: Dict[str, str]
    extraction_confidence: float
    raw_text: str = ""

class AdvancedTableExtractor:
    """Advanced table extractor with quality analysis and multiple extraction methods"""
    
    def __init__(self):
        self.config = config.extraction
        self._setup_ocr()
        
        # Quality analysis patterns
        self.meaningful_patterns = {
            'units': ['W', 'lm', 'lx', 'V', 'A', 'Hz', '°C', '°F', 'm', 'mm', 'cm', 'kg', 'g', 
                     's', 'min', 'h', 'day', 'week', 'month', 'year', '%', 'dB', 'cd', 'sr'],
            'technical_terms': ['efficacy', 'illuminance', 'luminous', 'luminaire', 'working', 'plane',
                              'calculation', 'building', 'room', 'story', 'floor', 'ceiling', 'wall',
                              'target', 'minimum', 'maximum', 'average', 'total', 'power', 'energy',
                              'lighting', 'design', 'specification', 'manufacturer', 'article', 'model'],
            'lighting_specific': ['lux', 'lumen', 'watt', 'candela', 'steradian', 'illuminance',
                                'luminance', 'brightness', 'glare', 'uniformity', 'efficacy',
                                'color temperature', 'CRI', 'UGR', 'power density']
        }
    
    def _setup_ocr(self):
        """Setup OCR configuration"""
        if OCR_AVAILABLE and self.config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd
    
    def extract_tables_from_pdf(self, pdf_path: Union[str, Path]) -> List[ExtractedTable]:
        """
        Extract all tables from PDF with quality analysis
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of ExtractedTable objects with quality metrics
        """
        pdf_path = Path(pdf_path)
        logger.info(f"Starting advanced table extraction from: {pdf_path}")
        
        all_tables = []
        
        # Method 1: Camelot (lattice and stream)
        if CAMELOT_AVAILABLE and self.config.use_camelot:
            camelot_tables = self._extract_with_camelot(pdf_path)
            all_tables.extend(camelot_tables)
            logger.info(f"Camelot extracted {len(camelot_tables)} tables")
        
        # Method 2: pdfplumber
        pdfplumber_tables = self._extract_with_pdfplumber(pdf_path)
        all_tables.extend(pdfplumber_tables)
        logger.info(f"pdfplumber extracted {len(pdfplumber_tables)} tables")
        
        # Method 3: OCR-based grid detection
        if OCR_AVAILABLE and self.config.use_ocr:
            ocr_tables = self._extract_with_ocr_grid(pdf_path)
            all_tables.extend(ocr_tables)
            logger.info(f"OCR grid extraction found {len(ocr_tables)} tables")
        
        # Quality filtering and deduplication
        quality_tables = self._filter_by_quality(all_tables)
        unique_tables = self._remove_duplicates(quality_tables)
        
        # Sort by quality score
        unique_tables.sort(key=lambda x: x.quality_metrics.overall_score, reverse=True)
        
        logger.info(f"Final result: {len(unique_tables)} high-quality unique tables")
        return unique_tables
    
    def _extract_with_camelot(self, pdf_path: Path) -> List[ExtractedTable]:
        """Extract tables using Camelot with both lattice and stream methods"""
        tables = []
        
        for flavor in self.config.camelot_flavors:
            try:
                camelot_tables = camelot.read_pdf(str(pdf_path), pages='all', flavor=flavor)
                
                for i, table in enumerate(camelot_tables):
                    if table.df is not None and not table.df.empty:
                        quality_metrics = self._analyze_table_quality(table.df)
                        
                        extracted_table = ExtractedTable(
                            dataframe=table.df,
                            source_method=f'camelot_{flavor}',
                            page_number=table.page,
                            table_index=i,
                            quality_metrics=quality_metrics,
                            headers=list(table.df.columns),
                            data_types=self._analyze_data_types(table.df),
                            extraction_confidence=table.accuracy / 100.0
                        )
                        tables.append(extracted_table)
            except Exception as e:
                logger.warning(f"Camelot {flavor} extraction failed: {e}")
        
        return tables
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[ExtractedTable]:
        """Extract tables using pdfplumber"""
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_tables = page.extract_tables()
                    
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            quality_metrics = self._analyze_table_quality(df)
                            
                            extracted_table = ExtractedTable(
                                dataframe=df,
                                source_method='pdfplumber',
                                page_number=page_num,
                                table_index=table_num,
                                quality_metrics=quality_metrics,
                                headers=table[0] if table else [],
                                data_types=self._analyze_data_types(df),
                                extraction_confidence=0.85,
                                raw_text=str(table)
                            )
                            tables.append(extracted_table)
                except Exception as e:
                    logger.warning(f"pdfplumber extraction failed for page {page_num}: {e}")
        
        return tables
    
    def _extract_with_ocr_grid(self, pdf_path: Path) -> List[ExtractedTable]:
        """Extract tables using OCR-based grid detection"""
        if not OCR_AVAILABLE:
            return []
        
        tables = []
        
        try:
            # Convert PDF to images
            pages = convert_from_path(pdf_path, dpi=self.config.ocr_dpi)
            
            for page_num, pil_img in enumerate(pages, 1):
                img = np.array(pil_img.convert("RGB"))[:, :, ::-1]
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Detect table grid
                dfs = self._image_to_cells_grid(gray)
                
                for i, df in enumerate(dfs):
                    if not df.empty:
                        quality_metrics = self._analyze_table_quality(df)
                        
                        extracted_table = ExtractedTable(
                            dataframe=df,
                            source_method='ocr_grid',
                            page_number=page_num,
                            table_index=i,
                            quality_metrics=quality_metrics,
                            headers=list(df.columns) if not df.empty else [],
                            data_types=self._analyze_data_types(df),
                            extraction_confidence=0.7
                        )
                        tables.append(extracted_table)
        except Exception as e:
            logger.warning(f"OCR grid extraction failed: {e}")
        
        return tables
    
    def _image_to_cells_grid(self, image: np.ndarray) -> List[pd.DataFrame]:
        """Convert image to table cells using grid detection"""
        img = image.copy()
        gray = cv2.equalizeHist(img)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 15, -2)
        thresh = 255 - thresh
        
        h, w = thresh.shape
        
        # Create kernels for line detection
        horiz_kernel_len = max(10, w // 30)
        vert_kernel_len = max(10, h // 50)
        
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horiz_kernel_len, 1))
        horizontal = cv2.erode(thresh, horizontal_kernel, iterations=1)
        horizontal = cv2.dilate(horizontal, horizontal_kernel, iterations=1)
        
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_kernel_len))
        vertical = cv2.erode(thresh, vertical_kernel, iterations=1)
        vertical = cv2.dilate(vertical, vertical_kernel, iterations=1)
        
        # Find intersections
        joint = cv2.bitwise_and(horizontal, vertical)
        
        # Connected components analysis
        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(joint, connectivity=8)
        if len(centroids) <= 2:
            return []
        
        # Extract grid coordinates
        xs = sorted(set(int(round(x)) for x in centroids[:, 0] if x > 0))
        ys = sorted(set(int(round(y)) for y in centroids[:, 1] if y > 0))
        
        # Cluster coordinates
        xs = self._cluster_coords(xs, tol=max(4, w//200))
        ys = self._cluster_coords(ys, tol=max(4, h//200))
        
        if len(xs) < 2 or len(ys) < 2:
            return []
        
        # Extract cell content
        rows = []
        for i in range(len(ys)-1):
            row_texts = []
            y1 = max(0, ys[i]-2)
            y2 = min(h, ys[i+1]+2)
            
            for j in range(len(xs)-1):
                x1 = max(0, xs[j]-2)
                x2 = min(w, xs[j+1]+2)
                cell_img = img[y1:y2, x1:x2]
                
                # Add padding
                pad_x = max(1, (x2-x1)//20)
                pad_y = max(1, (y2-y1)//20)
                crop = cell_img[pad_y: (y2-y1)-pad_y, pad_x: (x2-x1)-pad_x]
                
                if crop.size == 0:
                    text = ""
                else:
                    try:
                        text = pytesseract.image_to_string(crop, config=self.config.ocr_config).strip()
                    except Exception:
                        text = ""
                
                row_texts.append(text)
            rows.append(row_texts)
        
        df = pd.DataFrame(rows).map(lambda s: s.strip() if isinstance(s, str) else s)
        return [df] if not df.empty else []
    
    def _cluster_coords(self, coords: List[int], tol: int = 10) -> List[int]:
        """Cluster nearby coordinates"""
        if not coords:
            return []
        
        coords = sorted(coords)
        clustered = [coords[0]]
        
        for c in coords[1:]:
            if abs(c - clustered[-1]) <= tol:
                clustered[-1] = int(round((clustered[-1] + c) / 2.0))
            else:
                clustered.append(c)
        
        return clustered
    
    def _analyze_table_quality(self, df: pd.DataFrame) -> TableQualityMetrics:
        """Analyze table quality and return comprehensive metrics"""
        if df is None or df.empty:
            return TableQualityMetrics(0, 0, 0, 0, 0, 0, "Poor")
        
        # Basic metrics
        total = df.size
        non_empty = (df.astype(str).map(lambda s: s.strip() != "")).sum().sum()
        fill_ratio = non_empty / total if total > 0 else 0
        
        # Shape score
        rows, cols = df.shape
        if rows < 2 or cols < 2:
            shape_score = 0.0
        else:
            shape_score = min(1.0, max(0.0, (cols - 1) / 8.0))  # Prefer 2-8 columns
        
        # Content quality analysis
        content_score = self._analyze_content_quality(df)
        
        # Structure analysis
        structure_score = self._analyze_table_structure(df)
        
        # Noise detection
        noise_penalty = self._detect_ocr_noise(df)
        
        # Combined score
        overall_score = (0.3 * fill_ratio + 
                        0.2 * shape_score + 
                        0.3 * content_score + 
                        0.2 * structure_score - 
                        noise_penalty)
        
        overall_score = max(0.0, min(1.0, overall_score))
        
        # Confidence level
        if overall_score >= 0.8:
            confidence_level = "Excellent"
        elif overall_score >= 0.6:
            confidence_level = "Good"
        elif overall_score >= 0.4:
            confidence_level = "Fair"
        else:
            confidence_level = "Poor"
        
        return TableQualityMetrics(
            fill_ratio=fill_ratio,
            shape_score=shape_score,
            content_score=content_score,
            structure_score=structure_score,
            noise_penalty=noise_penalty,
            overall_score=overall_score,
            confidence_level=confidence_level
        )
    
    def _analyze_content_quality(self, df: pd.DataFrame) -> float:
        """Analyze the quality of content in the table"""
        if df.empty:
            return 0.0
        
        meaningful_patterns = 0
        total_cells = 0
        
        for col in df.columns:
            for val in df[col].dropna():
                val_str = str(val).strip()
                if not val_str:
                    continue
                
                total_cells += 1
                
                # Check for meaningful content
                if (self._contains_units(val_str) or 
                    self._contains_numbers(val_str) or 
                    self._contains_technical_terms(val_str) or
                    self._is_structured_text(val_str)):
                    meaningful_patterns += 1
        
        return meaningful_patterns / max(1, total_cells)
    
    def _contains_units(self, text: str) -> bool:
        """Check if text contains common units"""
        return any(unit in text for unit in self.meaningful_patterns['units'])
    
    def _contains_numbers(self, text: str) -> bool:
        """Check if text contains meaningful numbers"""
        number_patterns = [
            r'\d+\.\d+',  # decimal numbers
            r'\d+[eE][+-]?\d+',  # scientific notation
            r'\d+\s*[WlmVAdB°%]',  # numbers with units
            r'\d{2,}',  # numbers with 2+ digits
        ]
        return any(re.search(pattern, text) for pattern in number_patterns)
    
    def _contains_technical_terms(self, text: str) -> bool:
        """Check if text contains technical/engineering terms"""
        text_lower = text.lower()
        return any(term in text_lower for term in self.meaningful_patterns['technical_terms'])
    
    def _is_structured_text(self, text: str) -> bool:
        """Check if text appears to be structured (headers, labels, etc.)"""
        structured_patterns = [
            r'^[A-Z][a-z]+\s+[A-Z]',  # Title case with spaces
            r'^[A-Z]+$',  # All caps (likely headers)
            r'^\d+\.\s+',  # Numbered lists
            r'^[A-Z][a-z]+:',  # Labels with colons
        ]
        return any(re.match(pattern, text) for pattern in structured_patterns)
    
    def _analyze_table_structure(self, df: pd.DataFrame) -> float:
        """Analyze the structural quality of the table"""
        if df.empty:
            return 0.0
        
        # Check for consistent column structure
        non_empty_cols = 0
        for col in df.columns:
            if df[col].astype(str).str.strip().ne('').any():
                non_empty_cols += 1
        
        # Check for header-like first row
        has_headers = False
        if len(df) > 0:
            first_row = df.iloc[0].astype(str).str.strip()
            if first_row.str.len().mean() < 20 and first_row.str.len().max() < 50:
                has_headers = True
        
        # Check for data consistency in columns
        data_consistency = 0
        for col in df.columns:
            col_data = df[col].dropna().astype(str).str.strip()
            if len(col_data) > 1:
                numeric_count = col_data.str.contains(r'^\d+\.?\d*$').sum()
                if numeric_count / len(col_data) > 0.7:  # Mostly numeric
                    data_consistency += 1
                elif numeric_count / len(col_data) < 0.3:  # Mostly text
                    data_consistency += 1
        
        structure_score = (non_empty_cols / len(df.columns) * 0.4 + 
                          (1.0 if has_headers else 0.0) * 0.3 + 
                          data_consistency / max(1, len(df.columns)) * 0.3)
        
        return structure_score
    
    def _detect_ocr_noise(self, df: pd.DataFrame) -> float:
        """Detect OCR noise and artifacts"""
        if df.empty:
            return 0.0
        
        noise_indicators = 0
        total_cells = 0
        
        for col in df.columns:
            for val in df[col].dropna():
                val_str = str(val).strip()
                if not val_str:
                    continue
                
                total_cells += 1
                
                if self._is_ocr_noise(val_str):
                    noise_indicators += 1
        
        return noise_indicators / max(1, total_cells)
    
    def _is_ocr_noise(self, text: str) -> bool:
        """Check if text appears to be OCR noise"""
        noise_patterns = [
            r'^[^a-zA-Z0-9\s]{3,}$',  # Mostly special characters
            r'^[a-z]{1,2}$',  # Very short lowercase words
            r'^[^a-zA-Z0-9]*$',  # No alphanumeric characters
            r'^[a-zA-Z]{1}$',  # Single letters
            r'^[0-9,]{1,3}$',  # Just numbers and commas
            r'^[^a-zA-Z0-9\s\.\,\:\-\(\)]{2,}$',  # Random symbols
        ]
        
        if any(re.match(pattern, text) for pattern in noise_patterns):
            return True
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\.\,\:\-\(\)]', text)) / max(1, len(text))
        if special_char_ratio > 0.3:
            return True
        
        # Check for fragmented words
        if len(re.findall(r'[a-z]{1,2}[^a-zA-Z]', text)) > 2:
            return True
        
        return False
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze data types in each column"""
        data_types = {}
        
        for col in df.columns:
            col_data = df[col].dropna().astype(str).str.strip()
            
            if col_data.empty:
                data_types[col] = "empty"
                continue
            
            # Check if mostly numeric
            numeric_count = col_data.str.contains(r'^\d+\.?\d*$').sum()
            if numeric_count / len(col_data) > 0.7:
                data_types[col] = "numeric"
            # Check if contains units (lighting specific)
            elif any(unit in ' '.join(col_data) for unit in self.meaningful_patterns['units']):
                data_types[col] = "measurement"
            # Check if contains technical terms
            elif any(term in ' '.join(col_data).lower() for term in self.meaningful_patterns['technical_terms']):
                data_types[col] = "technical"
            else:
                data_types[col] = "text"
        
        return data_types
    
    def _filter_by_quality(self, tables: List[ExtractedTable]) -> List[ExtractedTable]:
        """Filter tables by quality thresholds"""
        quality_tables = []
        
        for table in tables:
            if (table.quality_metrics.overall_score >= self.config.min_table_score and
                table.dataframe.shape[0] >= self.config.min_rows and
                table.dataframe.shape[1] >= self.config.min_cols):
                quality_tables.append(table)
        
        return quality_tables
    
    def _remove_duplicates(self, tables: List[ExtractedTable]) -> List[ExtractedTable]:
        """Remove duplicate or very similar tables"""
        if not tables:
            return tables
        
        unique_tables = []
        
        for table in tables:
            is_duplicate = False
            
            for unique_table in unique_tables:
                if self._tables_are_similar(table.dataframe, unique_table.dataframe):
                    # Keep the one with higher quality score
                    if table.quality_metrics.overall_score > unique_table.quality_metrics.overall_score:
                        unique_tables.remove(unique_table)
                        unique_tables.append(table)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_tables.append(table)
        
        return unique_tables
    
    def _tables_are_similar(self, df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
        """Check if two tables are similar"""
        if df1.shape != df2.shape:
            return False
        
        matches = 0
        total_cells = df1.size
        
        for i in range(len(df1)):
            for j in range(len(df1.columns)):
                cell1 = str(df1.iloc[i, j]).strip()
                cell2 = str(df2.iloc[i, j]).strip()
                
                if cell1 == cell2 and cell1 != '':
                    matches += 1
                elif cell1 != '' and cell2 != '':
                    # Check for partial matches
                    if cell1 in cell2 or cell2 in cell1:
                        matches += 0.5
        
        similarity = matches / total_cells if total_cells > 0 else 0
        return similarity >= self.config.duplicate_similarity_threshold
    
    def export_tables(self, tables: List[ExtractedTable], output_dir: Union[str, Path], 
                     pdf_name: str) -> Dict[str, str]:
        """
        Export extracted tables to various formats
        
        Args:
            tables: List of extracted tables
            output_dir: Output directory
            pdf_name: Name of the source PDF (for file naming)
            
        Returns:
            Dictionary with paths to exported files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        exported_files = {}
        
        # Export individual CSV files
        csv_dir = output_dir / "tables_csv"
        csv_dir.mkdir(exist_ok=True)
        
        for i, table in enumerate(tables):
            csv_path = csv_dir / f"{pdf_name}_table_{i+1}_{table.source_method}.csv"
            table.dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
            exported_files[f"table_{i+1}_csv"] = str(csv_path)
        
        # Export combined Excel file
        excel_path = output_dir / f"{pdf_name}_all_tables.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                sheet_name = f"Table_{i+1}_{table.source_method[:10]}"
                table.dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        exported_files["excel_combined"] = str(excel_path)
        
        # Export quality report
        quality_report = self._generate_quality_report(tables, pdf_name)
        report_path = output_dir / f"{pdf_name}_table_quality_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(quality_report)
        exported_files["quality_report"] = str(report_path)
        
        return exported_files
    
    def _generate_quality_report(self, tables: List[ExtractedTable], pdf_name: str) -> str:
        """Generate quality report for extracted tables"""
        report = f"TABLE EXTRACTION QUALITY REPORT\n"
        report += f"================================\n"
        report += f"PDF: {pdf_name}\n"
        report += f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Tables Found: {len(tables)}\n\n"
        
        report += f"QUALITY THRESHOLDS:\n"
        report += f"- Minimum Score: {self.config.min_table_score}\n"
        report += f"- Minimum Rows: {self.config.min_rows}\n"
        report += f"- Minimum Columns: {self.config.min_cols}\n"
        report += f"- Duplicate Similarity Threshold: {self.config.duplicate_similarity_threshold}\n\n"
        
        report += f"TABLE DETAILS:\n"
        report += f"{'Rank':<4} {'Method':<15} {'Score':<6} {'Shape':<12} {'Quality':<10} {'Description'}\n"
        report += f"{'-'*4} {'-'*15} {'-'*6} {'-'*12} {'-'*10} {'-'*50}\n"
        
        for idx, table in enumerate(tables, 1):
            shape_str = f"{table.dataframe.shape[0]}x{table.dataframe.shape[1]}"
            description = self._get_table_description(table.dataframe)
            report += f"{idx:<4} {table.source_method:<15} {table.quality_metrics.overall_score:<6.2f} {shape_str:<12} {table.quality_metrics.confidence_level:<10} {description}\n"
        
        report += f"\nRECOMMENDATIONS:\n"
        report += f"- Tables with score > 0.7 are likely high-quality\n"
        report += f"- Tables with score 0.4-0.7 may need manual review\n"
        report += f"- Tables with score < 0.4 are likely low-quality or noise\n"
        
        return report
    
    def _get_table_description(self, df: pd.DataFrame) -> str:
        """Generate a brief description of the table content"""
        if df.empty:
            return "Empty table"
        
        # Get first few non-empty cells to understand content
        sample_text = []
        for col in df.columns:
            for val in df[col].dropna().head(2):
                val_str = str(val).strip()
                if val_str and len(val_str) < 50:
                    sample_text.append(val_str)
                if len(sample_text) >= 3:
                    break
            if len(sample_text) >= 3:
                break
        
        if not sample_text:
            return "No readable content"
        
        # Create description from sample text
        description = ", ".join(sample_text[:3])
        if len(description) > 50:
            description = description[:47] + "..."
        
        return description
