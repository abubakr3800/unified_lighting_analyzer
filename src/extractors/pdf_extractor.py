"""
Advanced PDF Text and Data Extraction
Combines multiple extraction methods for maximum coverage and accuracy
"""
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime

# PDF processing libraries
import pdfplumber
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract
from pdfminer.layout import LAParams

# Table extraction
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False

# OCR and image processing
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Data processing
import pandas as pd

try:
    from ..core.config import config
except ImportError:
    from core.config import config

logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Result of PDF extraction"""
    text: str
    tables: List[pd.DataFrame]
    images: List[str]
    metadata: Dict[str, Any]
    extraction_method: str
    confidence_score: float
    processing_time: float = 0.0

@dataclass
class TableInfo:
    """Information about extracted table"""
    dataframe: pd.DataFrame
    page_number: int
    extraction_method: str
    confidence_score: float
    table_type: str
    headers: List[str]

class PDFExtractor:
    """Advanced PDF extractor with multiple methods and fallbacks"""
    
    def __init__(self):
        self.config = config.extraction
        self._setup_ocr()
    
    def _setup_ocr(self):
        """Setup OCR configuration"""
        if OCR_AVAILABLE and self.config.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.config.tesseract_cmd
    
    def extract_from_pdf(self, pdf_path: Union[str, Path]) -> ExtractionResult:
        """
        Extract text, tables, and images from PDF using multiple methods
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with all extracted data
        """
        pdf_path = Path(pdf_path)
        start_time = datetime.now()
        
        logger.info(f"Starting extraction from: {pdf_path}")
        
        # Try different extraction methods
        results = []
        
        # Method 1: pdfplumber
        if self.config.use_pdfplumber:
            try:
                result = self._extract_with_pdfplumber(pdf_path)
                results.append(result)
                logger.info(f"pdfplumber extraction successful: {len(result.text)} chars, {len(result.tables)} tables")
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Method 2: PyMuPDF
        if self.config.use_pymupdf:
            try:
                result = self._extract_with_pymupdf(pdf_path)
                results.append(result)
                logger.info(f"PyMuPDF extraction successful: {len(result.text)} chars, {len(result.tables)} tables")
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}")
        
        # Method 3: pdfminer
        if self.config.use_pdfminer:
            try:
                result = self._extract_with_pdfminer(pdf_path)
                results.append(result)
                logger.info(f"pdfminer extraction successful: {len(result.text)} chars")
            except Exception as e:
                logger.warning(f"pdfminer extraction failed: {e}")
        
        # Method 4: OCR (if other methods fail or for scanned PDFs)
        if self.config.use_ocr and OCR_AVAILABLE:
            try:
                result = self._extract_with_ocr(pdf_path)
                results.append(result)
                logger.info(f"OCR extraction successful: {len(result.text)} chars")
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")
        
        # Combine results and select best
        if not results:
            raise Exception("All extraction methods failed")
        
        best_result = self._select_best_result(results)
        best_result.processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Extraction completed in {best_result.processing_time:.2f}s")
        return best_result
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> ExtractionResult:
        """Extract using pdfplumber"""
        text_parts = []
        tables = []
        images = []
        metadata = {}
        
        with pdfplumber.open(pdf_path) as pdf:
            metadata.update({
                'pages': len(pdf.pages),
                'title': pdf.metadata.get('Title', ''),
                'author': pdf.metadata.get('Author', ''),
                'subject': pdf.metadata.get('Subject', ''),
                'creator': pdf.metadata.get('Creator', ''),
                'producer': pdf.metadata.get('Producer', ''),
                'creation_date': pdf.metadata.get('CreationDate', ''),
                'modification_date': pdf.metadata.get('ModDate', '')
            })
            
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                
                # Extract tables
                page_tables = page.extract_tables()
                for table_num, table in enumerate(page_tables):
                    if table and len(table) > 1:  # At least header + 1 row
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df)
                
                # Extract images
                page_images = page.images
                for img_num, img in enumerate(page_images):
                    images.append(f"Page {page_num}, Image {img_num + 1}")
        
        return ExtractionResult(
            text='\n\n'.join(text_parts),
            tables=tables,
            images=images,
            metadata=metadata,
            extraction_method='pdfplumber',
            confidence_score=0.9
        )
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> ExtractionResult:
        """Extract using PyMuPDF"""
        text_parts = []
        tables = []
        images = []
        metadata = {}
        
        doc = fitz.open(pdf_path)
        metadata.update({
            'pages': doc.page_count,
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'subject': doc.metadata.get('subject', ''),
            'creator': doc.metadata.get('creator', ''),
            'producer': doc.metadata.get('producer', ''),
            'creation_date': doc.metadata.get('creationDate', ''),
            'modification_date': doc.metadata.get('modDate', '')
        })
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Extract text
            page_text = page.get_text()
            if page_text:
                text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            # Extract tables (basic approach)
            tables_found = self._extract_tables_pymupdf(page, page_num + 1)
            tables.extend(tables_found)
            
            # Extract images
            image_list = page.get_images()
            for img_num, img in enumerate(image_list):
                images.append(f"Page {page_num + 1}, Image {img_num + 1}")
        
        doc.close()
        
        return ExtractionResult(
            text='\n\n'.join(text_parts),
            tables=tables,
            images=images,
            metadata=metadata,
            extraction_method='pymupdf',
            confidence_score=0.85
        )
    
    def _extract_with_pdfminer(self, pdf_path: Path) -> ExtractionResult:
        """Extract using pdfminer"""
        try:
            text = pdfminer_extract(str(pdf_path), laparams=LAParams())
            return ExtractionResult(
                text=text,
                tables=[],
                images=[],
                metadata={'extraction_method': 'pdfminer'},
                extraction_method='pdfminer',
                confidence_score=0.8
            )
        except Exception as e:
            logger.error(f"pdfminer extraction failed: {e}")
            return ExtractionResult(
                text="",
                tables=[],
                images=[],
                metadata={},
                extraction_method='pdfminer',
                confidence_score=0.0
            )
    
    def _extract_with_ocr(self, pdf_path: Path) -> ExtractionResult:
        """Extract using OCR"""
        if not OCR_AVAILABLE:
            raise Exception("OCR libraries not available")
        
        text_parts = []
        images = []
        
        # Convert PDF to images
        pages = convert_from_path(pdf_path, dpi=self.config.ocr_dpi)
        
        for page_num, page in enumerate(pages, 1):
            # Save temporary image
            temp_img_path = f"temp_page_{page_num}.png"
            page.save(temp_img_path, 'PNG')
            images.append(temp_img_path)
            
            # Extract text using OCR
            try:
                text = pytesseract.image_to_string(page, config=self.config.ocr_config)
                if text.strip():
                    text_parts.append(f"--- Page {page_num} (OCR) ---\n{text}")
            except Exception as e:
                logger.warning(f"OCR failed for page {page_num}: {e}")
        
        return ExtractionResult(
            text='\n\n'.join(text_parts),
            tables=[],
            images=images,
            metadata={'extraction_method': 'ocr', 'dpi': self.config.ocr_dpi},
            extraction_method='ocr',
            confidence_score=0.7
        )
    
    def _extract_tables_pymupdf(self, page, page_num: int) -> List[pd.DataFrame]:
        """Extract tables from PyMuPDF page"""
        tables = []
        try:
            # Get text blocks
            blocks = page.get_text("dict")
            
            # Simple table detection based on text alignment
            # This is a basic implementation - could be enhanced
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    lines = block["lines"]
                    if len(lines) > 1:
                        # Check if this looks like a table
                        table_data = []
                        for line in lines:
                            line_text = ""
                            for span in line.get("spans", []):
                                line_text += span.get("text", "")
                            if line_text.strip():
                                table_data.append([line_text.strip()])
                        
                        if len(table_data) > 1:
                            df = pd.DataFrame(table_data)
                            tables.append(df)
        except Exception as e:
            logger.warning(f"Table extraction failed for page {page_num}: {e}")
        
        return tables
    
    def _select_best_result(self, results: List[ExtractionResult]) -> ExtractionResult:
        """Select the best extraction result based on quality metrics"""
        if len(results) == 1:
            return results[0]
        
        # Score each result
        scored_results = []
        for result in results:
            score = self._calculate_result_score(result)
            scored_results.append((score, result))
        
        # Return the result with highest score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1]
    
    def _calculate_result_score(self, result: ExtractionResult) -> float:
        """Calculate quality score for extraction result"""
        score = 0.0
        
        # Text length score (normalized)
        text_length = len(result.text)
        if text_length > 0:
            score += min(1.0, text_length / 10000) * 0.4
        
        # Table count score
        table_count = len(result.tables)
        if table_count > 0:
            score += min(1.0, table_count / 10) * 0.3
        
        # Method confidence score
        score += result.confidence_score * 0.3
        
        return score
    
    def extract_tables_advanced(self, pdf_path: Union[str, Path]) -> List[TableInfo]:
        """
        Advanced table extraction using multiple methods
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of TableInfo objects with extracted tables
        """
        pdf_path = Path(pdf_path)
        all_tables = []
        
        # Method 1: Camelot
        if CAMELOT_AVAILABLE and self.config.use_camelot:
            try:
                camelot_tables = self._extract_tables_camelot(pdf_path)
                all_tables.extend(camelot_tables)
                logger.info(f"Camelot extracted {len(camelot_tables)} tables")
            except Exception as e:
                logger.warning(f"Camelot table extraction failed: {e}")
        
        # Method 2: Tabula
        if TABULA_AVAILABLE and self.config.use_tabula:
            try:
                tabula_tables = self._extract_tables_tabula(pdf_path)
                all_tables.extend(tabula_tables)
                logger.info(f"Tabula extracted {len(tabula_tables)} tables")
            except Exception as e:
                logger.warning(f"Tabula table extraction failed: {e}")
        
        # Method 3: pdfplumber tables
        try:
            pdfplumber_tables = self._extract_tables_pdfplumber(pdf_path)
            all_tables.extend(pdfplumber_tables)
            logger.info(f"pdfplumber extracted {len(pdfplumber_tables)} tables")
        except Exception as e:
            logger.warning(f"pdfplumber table extraction failed: {e}")
        
        # Filter and deduplicate tables
        filtered_tables = self._filter_and_deduplicate_tables(all_tables)
        
        logger.info(f"Total tables after filtering: {len(filtered_tables)}")
        return filtered_tables
    
    def _extract_tables_camelot(self, pdf_path: Path) -> List[TableInfo]:
        """Extract tables using Camelot"""
        tables = []
        
        for flavor in self.config.camelot_flavors:
            try:
                camelot_tables = camelot.read_pdf(str(pdf_path), flavor=flavor, pages='all')
                
                for i, table in enumerate(camelot_tables):
                    if table.df is not None and not table.df.empty:
                        table_info = TableInfo(
                            dataframe=table.df,
                            page_number=table.page,
                            extraction_method=f'camelot_{flavor}',
                            confidence_score=table.accuracy / 100.0,
                            table_type='structured',
                            headers=list(table.df.columns) if not table.df.empty else []
                        )
                        tables.append(table_info)
            except Exception as e:
                logger.warning(f"Camelot {flavor} extraction failed: {e}")
        
        return tables
    
    def _extract_tables_tabula(self, pdf_path: Path) -> List[TableInfo]:
        """Extract tables using Tabula"""
        tables = []
        
        try:
            tabula_tables = tabula.read_pdf(str(pdf_path), pages='all', multiple_tables=True)
            
            for i, df in enumerate(tabula_tables):
                if df is not None and not df.empty:
                    table_info = TableInfo(
                        dataframe=df,
                        page_number=1,  # Tabula doesn't provide page info easily
                        extraction_method='tabula',
                        confidence_score=0.8,  # Default confidence
                        table_type='structured',
                        headers=list(df.columns) if not df.empty else []
                    )
                    tables.append(table_info)
        except Exception as e:
            logger.warning(f"Tabula extraction failed: {e}")
        
        return tables
    
    def _extract_tables_pdfplumber(self, pdf_path: Path) -> List[TableInfo]:
        """Extract tables using pdfplumber"""
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_tables = page.extract_tables()
                
                for table_num, table in enumerate(page_tables):
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        
                        table_info = TableInfo(
                            dataframe=df,
                            page_number=page_num,
                            extraction_method='pdfplumber',
                            confidence_score=0.85,
                            table_type='text_based',
                            headers=table[0] if table else []
                        )
                        tables.append(table_info)
        
        return tables
    
    def _filter_and_deduplicate_tables(self, tables: List[TableInfo]) -> List[TableInfo]:
        """Filter and deduplicate extracted tables"""
        # Filter by quality
        quality_tables = []
        for table in tables:
            if self._is_quality_table(table.dataframe):
                quality_tables.append(table)
        
        # Remove duplicates
        unique_tables = self._remove_duplicate_tables(quality_tables)
        
        return unique_tables
    
    def _is_quality_table(self, df: pd.DataFrame) -> bool:
        """Check if table meets quality criteria"""
        if df is None or df.empty:
            return False
        
        rows, cols = df.shape
        if rows < self.config.min_rows or cols < self.config.min_cols:
            return False
        
        # Check for meaningful content
        non_empty_cells = df.astype(str).apply(lambda x: x.str.strip() != "").sum().sum()
        total_cells = df.size
        fill_ratio = non_empty_cells / total_cells if total_cells > 0 else 0
        
        return fill_ratio >= 0.3  # At least 30% filled cells
    
    def _remove_duplicate_tables(self, tables: List[TableInfo]) -> List[TableInfo]:
        """Remove duplicate or very similar tables"""
        if not tables:
            return tables
        
        unique_tables = []
        for table in tables:
            is_duplicate = False
            
            for unique_table in unique_tables:
                if self._tables_are_similar(table.dataframe, unique_table.dataframe):
                    # Keep the one with higher confidence
                    if table.confidence_score > unique_table.confidence_score:
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
        
        # Compare cell by cell
        matches = 0
        total_cells = df1.size
        
        for i in range(len(df1)):
            for j in range(len(df1.columns)):
                cell1 = str(df1.iloc[i, j]).strip()
                cell2 = str(df2.iloc[i, j]).strip()
                
                if cell1 == cell2 and cell1 != '':
                    matches += 1
        
        similarity = matches / total_cells if total_cells > 0 else 0
        return similarity >= self.config.duplicate_similarity_threshold
