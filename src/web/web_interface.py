"""
Unified Web Interface for Lighting Analyzer
Streamlit-based interface for all features
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Import our modules
from ..core.config import config
from ..extractors.pdf_extractor import PDFExtractor
from ..extractors.table_extractor import AdvancedTableExtractor
from ..standards.standards_processor import StandardsProcessor, StandardType, RoomType
from ..analyzers.dialux_analyzer import DialuxAnalyzer

logger = logging.getLogger(__name__)

class UnifiedWebInterface:
    """Unified web interface for all lighting analyzer features"""
    
    def __init__(self):
        self.config = config.web
        self.pdf_extractor = PDFExtractor()
        self.table_extractor = AdvancedTableExtractor()
        self.standards_processor = StandardsProcessor()
        self.dialux_analyzer = DialuxAnalyzer()
        
        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
    
    def run(self):
        """Run the web interface"""
        st.set_page_config(
            page_title=self.config.page_title,
            page_icon=self.config.page_icon,
            layout=self.config.layout,
            initial_sidebar_state="expanded"
        )
        
        # Main title
        st.title("💡 Unified Lighting Analyzer")
        st.markdown("**Comprehensive analysis of lighting documents, standards, and Dialux reports**")
        
        # Sidebar navigation
        self._render_sidebar()
        
        # Main content based on selection
        page = st.session_state.get('current_page', 'home')
        
        if page == 'home':
            self._render_home_page()
        elif page == 'pdf_extraction':
            self._render_pdf_extraction_page()
        elif page == 'table_extraction':
            self._render_table_extraction_page()
        elif page == 'standards_processing':
            self._render_standards_processing_page()
        elif page == 'dialux_analysis':
            self._render_dialux_analysis_page()
        elif page == 'comparison':
            self._render_comparison_page()
        elif page == 'settings':
            self._render_settings_page()
    
    def _render_sidebar(self):
        """Render sidebar navigation"""
        st.sidebar.title("🧭 Navigation")
        
        pages = {
            "🏠 Home": "home",
            "📄 PDF Extraction": "pdf_extraction",
            "📊 Table Extraction": "table_extraction",
            "📋 Standards Processing": "standards_processing",
            "🔍 Dialux Analysis": "dialux_analysis",
            "⚖️ Comparison": "comparison",
            "⚙️ Settings": "settings"
        }
        
        for page_name, page_key in pages.items():
            if st.sidebar.button(page_name, key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.sidebar.markdown("---")
        
        # File upload section
        st.sidebar.subheader("📁 Upload Files")
        uploaded_file = st.sidebar.file_uploader(
            "Upload PDF",
            type=['pdf'],
            help="Upload a PDF file for analysis"
        )
        
        if uploaded_file:
            file_key = uploaded_file.name
            if file_key not in st.session_state.uploaded_files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    shutil.copyfileobj(uploaded_file, tmp_file)
                    st.session_state.uploaded_files[file_key] = tmp_file.name
                
                st.sidebar.success(f"✅ {file_key} uploaded successfully!")
        
        # Display uploaded files
        if st.session_state.uploaded_files:
            st.sidebar.subheader("📂 Uploaded Files")
            for file_name in st.session_state.uploaded_files.keys():
                st.sidebar.text(f"• {file_name}")
    
    def _render_home_page(self):
        """Render home page"""
        st.header("🏠 Welcome to Unified Lighting Analyzer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Features")
            st.markdown("""
            - **PDF Text Extraction**: Multi-method PDF text extraction with fallbacks
            - **Advanced Table Extraction**: High-quality table extraction with quality analysis
            - **Standards Processing**: Process and compare lighting standards documents
            - **Dialux Analysis**: Comprehensive Dialux report analysis and compliance checking
            - **Standards Comparison**: Compare different lighting standards
            - **Compliance Checking**: Check compliance against multiple standards
            """)
        
        with col2:
            st.subheader("🚀 Quick Start")
            st.markdown("""
            1. **Upload a PDF** using the sidebar
            2. **Choose your analysis type** from the navigation menu
            3. **Configure settings** if needed
            4. **Run analysis** and view results
            5. **Export results** in various formats
            """)
        
        st.subheader("📊 System Status")
        self._render_system_status()
        
        st.subheader("📈 Recent Analysis")
        self._render_recent_analysis()
    
    def _render_pdf_extraction_page(self):
        """Render PDF extraction page"""
        st.header("📄 PDF Text Extraction")
        st.markdown("Extract text and metadata from PDF documents using multiple methods")
        
        # File selection
        uploaded_files = list(st.session_state.uploaded_files.keys())
        if not uploaded_files:
            st.warning("Please upload a PDF file first using the sidebar")
            return
        
        selected_file = st.selectbox("Select PDF file", uploaded_files)
        
        if st.button("🔍 Extract Text", type="primary"):
            with st.spinner("Extracting text from PDF..."):
                try:
                    file_path = st.session_state.uploaded_files[selected_file]
                    result = self.pdf_extractor.extract_from_pdf(file_path)
                    
                    # Store result
                    st.session_state.analysis_results[f"pdf_extraction_{selected_file}"] = result
                    
                    st.success("✅ Text extraction completed!")
                    
                    # Display results
                    self._display_pdf_extraction_results(result)
                    
                except Exception as e:
                    st.error(f"❌ Extraction failed: {e}")
                    logger.error(f"PDF extraction failed: {e}")
    
    def _render_table_extraction_page(self):
        """Render table extraction page"""
        st.header("📊 Advanced Table Extraction")
        st.markdown("Extract tables from PDFs with quality analysis and multiple extraction methods")
        
        # File selection
        uploaded_files = list(st.session_state.uploaded_files.keys())
        if not uploaded_files:
            st.warning("Please upload a PDF file first using the sidebar")
            return
        
        selected_file = st.selectbox("Select PDF file", uploaded_files)
        
        # Configuration options
        st.subheader("⚙️ Extraction Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            min_score = st.slider("Minimum Quality Score", 0.0, 1.0, 0.3, 0.1)
            min_rows = st.number_input("Minimum Rows", 1, 20, 2)
        
        with col2:
            min_cols = st.number_input("Minimum Columns", 1, 20, 2)
            duplicate_threshold = st.slider("Duplicate Threshold", 0.0, 1.0, 0.8, 0.1)
        
        if st.button("🔍 Extract Tables", type="primary"):
            with st.spinner("Extracting tables from PDF..."):
                try:
                    file_path = st.session_state.uploaded_files[selected_file]
                    
                    # Update config
                    self.table_extractor.config.min_table_score = min_score
                    self.table_extractor.config.min_rows = min_rows
                    self.table_extractor.config.min_cols = min_cols
                    self.table_extractor.config.duplicate_similarity_threshold = duplicate_threshold
                    
                    tables = self.table_extractor.extract_tables_from_pdf(file_path)
                    
                    # Store result
                    st.session_state.analysis_results[f"table_extraction_{selected_file}"] = tables
                    
                    st.success(f"✅ Table extraction completed! Found {len(tables)} tables")
                    
                    # Display results
                    self._display_table_extraction_results(tables, selected_file)
                    
                except Exception as e:
                    st.error(f"❌ Table extraction failed: {e}")
                    logger.error(f"Table extraction failed: {e}")
    
    def _render_standards_processing_page(self):
        """Render standards processing page"""
        st.header("📋 Standards Processing")
        st.markdown("Process lighting standards documents and build compliance database")
        
        # File selection
        uploaded_files = list(st.session_state.uploaded_files.keys())
        if not uploaded_files:
            st.warning("Please upload a PDF file first using the sidebar")
            return
        
        selected_file = st.selectbox("Select Standards PDF", uploaded_files)
        
        if st.button("🔍 Process Standards", type="primary"):
            with st.spinner("Processing standards document..."):
                try:
                    file_path = st.session_state.uploaded_files[selected_file]
                    standards_doc = self.standards_processor.process_standards_document(file_path)
                    
                    # Store result
                    st.session_state.analysis_results[f"standards_{selected_file}"] = standards_doc
                    
                    st.success("✅ Standards processing completed!")
                    
                    # Display results
                    self._display_standards_results(standards_doc)
                    
                except Exception as e:
                    st.error(f"❌ Standards processing failed: {e}")
                    logger.error(f"Standards processing failed: {e}")
        
        # Standards database section
        st.subheader("📚 Standards Database")
        self._display_standards_database()
    
    def _render_dialux_analysis_page(self):
        """Render Dialux analysis page"""
        st.header("🔍 Dialux Report Analysis")
        st.markdown("Comprehensive analysis of Dialux reports with compliance checking")
        
        # File selection
        uploaded_files = list(st.session_state.uploaded_files.keys())
        if not uploaded_files:
            st.warning("Please upload a PDF file first using the sidebar")
            return
        
        selected_file = st.selectbox("Select Dialux Report", uploaded_files)
        
        # Analysis options
        st.subheader("⚙️ Analysis Options")
        col1, col2 = st.columns(2)
        
        with col1:
            standards_to_check = st.multiselect(
                "Standards to Check",
                [s.value for s in StandardType],
                default=[StandardType.EN_12464_1.value]
            )
            
            include_visualizations = st.checkbox("Include Visualizations", True)
        
        with col2:
            export_formats = st.multiselect(
                "Export Formats",
                ["json", "csv", "xlsx", "pdf"],
                default=["json", "csv"]
            )
            
            detailed_report = st.checkbox("Generate Detailed Report", True)
        
        if st.button("🔍 Analyze Dialux Report", type="primary"):
            with st.spinner("Analyzing Dialux report..."):
                try:
                    file_path = st.session_state.uploaded_files[selected_file]
                    analysis_result = self.dialux_analyzer.analyze_dialux_report(file_path)
                    
                    # Store result
                    st.session_state.analysis_results[f"dialux_{selected_file}"] = analysis_result
                    
                    st.success("✅ Dialux analysis completed!")
                    
                    # Display results
                    self._display_dialux_results(analysis_result, include_visualizations)
                    
                except Exception as e:
                    st.error(f"❌ Dialux analysis failed: {e}")
                    logger.error(f"Dialux analysis failed: {e}")
    
    def _render_comparison_page(self):
        """Render comparison page"""
        st.header("⚖️ Standards Comparison")
        st.markdown("Compare different lighting standards and analyze differences")
        
        # Standards selection
        col1, col2 = st.columns(2)
        
        with col1:
            standard_a = st.selectbox(
                "Standard A",
                [s.value for s in StandardType],
                key="standard_a"
            )
        
        with col2:
            standard_b = st.selectbox(
                "Standard B",
                [s.value for s in StandardType],
                key="standard_b"
            )
        
        # Room type selection
        room_type = st.selectbox(
            "Room Type",
            [r.value for r in RoomType]
        )
        
        if st.button("🔍 Compare Standards", type="primary"):
            with st.spinner("Comparing standards..."):
                try:
                    standard_a_enum = StandardType(standard_a)
                    standard_b_enum = StandardType(standard_b)
                    room_type_enum = RoomType(room_type)
                    
                    comparisons = self.standards_processor.compare_standards(
                        standard_a_enum, standard_b_enum, room_type_enum
                    )
                    
                    # Store result
                    comparison_key = f"comparison_{standard_a}_{standard_b}_{room_type}"
                    st.session_state.analysis_results[comparison_key] = comparisons
                    
                    st.success("✅ Standards comparison completed!")
                    
                    # Display results
                    self._display_comparison_results(comparisons, standard_a, standard_b, room_type)
                    
                except Exception as e:
                    st.error(f"❌ Standards comparison failed: {e}")
                    logger.error(f"Standards comparison failed: {e}")
    
    def _render_settings_page(self):
        """Render settings page"""
        st.header("⚙️ Settings")
        st.markdown("Configure system settings and parameters")
        
        # Extraction settings
        st.subheader("📄 Extraction Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Use pdfplumber", value=self.config.extraction.use_pdfplumber)
            st.checkbox("Use PyMuPDF", value=self.config.extraction.use_pymupdf)
            st.checkbox("Use pdfminer", value=self.config.extraction.use_pdfminer)
        
        with col2:
            st.checkbox("Use Camelot", value=self.config.extraction.use_camelot)
            st.checkbox("Use Tabula", value=self.config.extraction.use_tabula)
            st.checkbox("Use OCR", value=self.config.extraction.use_ocr)
        
        # Quality thresholds
        st.subheader("📊 Quality Thresholds")
        col1, col2 = st.columns(2)
        
        with col1:
            min_score = st.slider("Minimum Table Score", 0.0, 1.0, self.config.extraction.min_table_score, 0.1)
            min_rows = st.number_input("Minimum Rows", 1, 20, self.config.extraction.min_rows)
        
        with col2:
            min_cols = st.number_input("Minimum Columns", 1, 20, self.config.extraction.min_cols)
            duplicate_threshold = st.slider("Duplicate Threshold", 0.0, 1.0, self.config.extraction.duplicate_similarity_threshold, 0.1)
        
        # Standards settings
        st.subheader("📋 Standards Settings")
        similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, self.config.standards.similarity_threshold, 0.1)
        compliance_threshold = st.slider("Compliance Threshold", 0.0, 1.0, self.config.standards.compliance_threshold, 0.1)
        
        if st.button("💾 Save Settings", type="primary"):
            # Update config
            self.config.extraction.min_table_score = min_score
            self.config.extraction.min_rows = min_rows
            self.config.extraction.min_cols = min_cols
            self.config.extraction.duplicate_similarity_threshold = duplicate_threshold
            self.config.standards.similarity_threshold = similarity_threshold
            self.config.standards.compliance_threshold = compliance_threshold
            
            st.success("✅ Settings saved successfully!")
    
    def _render_system_status(self):
        """Render system status"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PDF Extractor", "✅ Ready")
        
        with col2:
            st.metric("Table Extractor", "✅ Ready")
        
        with col3:
            st.metric("Standards Processor", "✅ Ready")
        
        with col4:
            st.metric("Dialux Analyzer", "✅ Ready")
    
    def _render_recent_analysis(self):
        """Render recent analysis results"""
        if not st.session_state.analysis_results:
            st.info("No analysis results yet. Upload a file and run an analysis to see results here.")
            return
        
        # Display recent results
        for key, result in list(st.session_state.analysis_results.items())[-5:]:
            with st.expander(f"📊 {key}"):
                if "pdf_extraction" in key:
                    st.text(f"Text length: {len(result.text)} characters")
                    st.text(f"Tables found: {len(result.tables)}")
                    st.text(f"Extraction method: {result.extraction_method}")
                elif "table_extraction" in key:
                    st.text(f"Tables extracted: {len(result)}")
                    if result:
                        st.text(f"Average quality score: {sum(t.quality_metrics.overall_score for t in result) / len(result):.2f}")
                elif "dialux" in key:
                    st.text(f"Project: {result.report.project_name}")
                    st.text(f"Rooms: {result.report.total_rooms}")
                    st.text(f"Compliance: {result.report.overall_compliance_rate:.1%}")
    
    def _display_pdf_extraction_results(self, result):
        """Display PDF extraction results"""
        st.subheader("📄 Extraction Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Text Length", f"{len(result.text):,} characters")
            st.metric("Tables Found", len(result.tables))
            st.metric("Images Found", len(result.images))
        
        with col2:
            st.metric("Extraction Method", result.extraction_method)
            st.metric("Confidence Score", f"{result.confidence_score:.2f}")
            st.metric("Processing Time", f"{result.processing_time:.2f}s")
        
        # Display metadata
        if result.metadata:
            st.subheader("📋 Document Metadata")
            metadata_df = pd.DataFrame(list(result.metadata.items()), columns=["Property", "Value"])
            st.dataframe(metadata_df, use_container_width=True)
        
        # Display text preview
        st.subheader("📝 Text Preview")
        text_preview = result.text[:2000] + "..." if len(result.text) > 2000 else result.text
        st.text_area("Extracted Text", text_preview, height=300)
        
        # Download options
        st.subheader("💾 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download Text"):
                st.download_button(
                    label="Download as TXT",
                    data=result.text,
                    file_name="extracted_text.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📊 Download Metadata"):
                metadata_json = json.dumps(result.metadata, indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=metadata_json,
                    file_name="metadata.json",
                    mime="application/json"
                )
    
    def _display_table_extraction_results(self, tables, filename):
        """Display table extraction results"""
        st.subheader("📊 Table Extraction Results")
        
        if not tables:
            st.warning("No tables found in the document")
            return
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tables", len(tables))
        
        with col2:
            avg_score = sum(t.quality_metrics.overall_score for t in tables) / len(tables)
            st.metric("Average Quality", f"{avg_score:.2f}")
        
        with col3:
            high_quality = sum(1 for t in tables if t.quality_metrics.overall_score > 0.7)
            st.metric("High Quality", high_quality)
        
        with col4:
            total_cells = sum(t.dataframe.size for t in tables)
            st.metric("Total Cells", f"{total_cells:,}")
        
        # Quality distribution
        st.subheader("📈 Quality Distribution")
        quality_scores = [t.quality_metrics.overall_score for t in tables]
        fig = px.histogram(x=quality_scores, nbins=20, title="Table Quality Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Table details
        st.subheader("📋 Table Details")
        for i, table in enumerate(tables):
            with st.expander(f"Table {i+1} - {table.source_method} (Score: {table.quality_metrics.overall_score:.2f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text(f"Shape: {table.dataframe.shape}")
                    st.text(f"Page: {table.page_number}")
                    st.text(f"Method: {table.source_method}")
                    st.text(f"Confidence: {table.extraction_confidence:.2f}")
                
                with col2:
                    st.text(f"Quality Level: {table.quality_metrics.confidence_level}")
                    st.text(f"Fill Ratio: {table.quality_metrics.fill_ratio:.2f}")
                    st.text(f"Content Score: {table.quality_metrics.content_score:.2f}")
                    st.text(f"Structure Score: {table.quality_metrics.structure_score:.2f}")
                
                # Display table
                st.dataframe(table.dataframe, use_container_width=True)
                
                # Download button
                csv_data = table.dataframe.to_csv(index=False)
                st.download_button(
                    label=f"Download Table {i+1} as CSV",
                    data=csv_data,
                    file_name=f"{filename}_table_{i+1}.csv",
                    mime="text/csv"
                )
    
    def _display_standards_results(self, standards_doc):
        """Display standards processing results"""
        st.subheader("📋 Standards Processing Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Standard Type", standards_doc.standard_type.value)
            st.metric("Version", standards_doc.version)
            st.metric("Language", standards_doc.language)
        
        with col2:
            st.metric("Requirements Found", len(standards_doc.requirements))
            st.metric("Tables Extracted", len(standards_doc.tables))
            st.metric("Text Length", f"{len(standards_doc.text_content):,} chars")
        
        # Requirements summary
        if standards_doc.requirements:
            st.subheader("📊 Requirements Summary")
            req_data = []
            for req in standards_doc.requirements:
                req_data.append({
                    "Parameter": req.parameter,
                    "Value": req.value,
                    "Unit": req.unit,
                    "Condition": req.condition,
                    "Room Type": req.room_type.value,
                    "Description": req.description
                })
            
            req_df = pd.DataFrame(req_data)
            st.dataframe(req_df, use_container_width=True)
        
        # Download options
        st.subheader("💾 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Download Requirements"):
                req_json = json.dumps([req.__dict__ for req in standards_doc.requirements], indent=2, default=str)
                st.download_button(
                    label="Download as JSON",
                    data=req_json,
                    file_name="requirements.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Download Summary"):
                summary_data = {
                    "name": standards_doc.name,
                    "standard_type": standards_doc.standard_type.value,
                    "version": standards_doc.version,
                    "language": standards_doc.language,
                    "requirements_count": len(standards_doc.requirements),
                    "tables_count": len(standards_doc.tables)
                }
                summary_json = json.dumps(summary_data, indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=summary_json,
                    file_name="summary.json",
                    mime="application/json"
                )
    
    def _display_standards_database(self):
        """Display standards database"""
        summary = self.standards_processor.get_standards_summary()
        
        st.metric("Total Standards", summary["total_standards"])
        
        if summary["standards"]:
            st.subheader("📚 Available Standards")
            for standard_key, standard_info in summary["standards"].items():
                with st.expander(f"📋 {standard_info['name']} (v{standard_info['version']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text(f"Room Types: {len(standard_info['room_types'])}")
                        st.text(f"Total Requirements: {standard_info['total_requirements']}")
                    
                    with col2:
                        st.text("Room Types:")
                        for room_type in standard_info['room_types']:
                            st.text(f"• {room_type}")
    
    def _display_dialux_results(self, analysis_result, include_visualizations=True):
        """Display Dialux analysis results"""
        report = analysis_result.report
        
        st.subheader("🔍 Dialux Analysis Results")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Project", report.project_name)
            st.metric("Total Rooms", report.total_rooms)
        
        with col2:
            st.metric("Total Area", f"{report.total_area:.1f} m²")
            st.metric("Compliance Rate", f"{report.overall_compliance_rate:.1%}")
        
        with col3:
            st.metric("Data Quality", f"{report.data_quality_score:.1%}")
            st.metric("Best Standard", report.best_matching_standard.value if report.best_matching_standard else "N/A")
        
        with col4:
            st.metric("Avg Illuminance", f"{report.overall_illuminance_avg:.0f} lux")
            st.metric("Avg Uniformity", f"{report.overall_uniformity_avg:.2f}")
        
        # Visualizations
        if include_visualizations and report.rooms:
            st.subheader("📊 Visualizations")
            
            # Compliance by room
            room_names = [room.name for room in report.rooms]
            compliance_rates = [report.standards_compliance.get(room.name, 0) for room in report.rooms]
            
            fig = px.bar(
                x=room_names, 
                y=compliance_rates,
                title="Compliance Rate by Room",
                labels={"x": "Room", "y": "Compliance Rate"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Parameter distribution
            param_data = []
            for room in report.rooms:
                if room.illuminance_avg:
                    param_data.append({"Room": room.name, "Parameter": "Illuminance", "Value": room.illuminance_avg})
                if room.uniformity:
                    param_data.append({"Room": room.name, "Parameter": "Uniformity", "Value": room.uniformity})
                if room.ugr:
                    param_data.append({"Room": room.name, "Parameter": "UGR", "Value": room.ugr})
            
            if param_data:
                param_df = pd.DataFrame(param_data)
                fig = px.box(param_df, x="Parameter", y="Value", title="Parameter Distribution by Room")
                st.plotly_chart(fig, use_container_width=True)
        
        # Room details
        st.subheader("🏠 Room Details")
        for room in report.rooms:
            with st.expander(f"🏠 {room.name} ({room.room_type.value})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text(f"Area: {room.area:.1f} m²")
                    st.text(f"Data Completeness: {room.data_completeness:.1%}")
                    st.text(f"Confidence: {room.confidence_score:.1%}")
                
                with col2:
                    if room.illuminance_avg:
                        st.text(f"Illuminance: {room.illuminance_avg:.0f} lux")
                    if room.uniformity:
                        st.text(f"Uniformity: {room.uniformity:.2f}")
                    if room.ugr:
                        st.text(f"UGR: {room.ugr:.1f}")
                    if room.power_density:
                        st.text(f"Power Density: {room.power_density:.1f} W/m²")
                
                # Compliance results
                if room.compliance_results:
                    st.subheader("✅ Compliance Results")
                    for result in room.compliance_results:
                        status = "✅" if result.is_compliant else "❌"
                        st.text(f"{status} {result.parameter}: {result.actual_value} {result.unit} (required: {result.required_value} {result.unit})")
        
        # Recommendations
        if analysis_result.recommendations:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(analysis_result.recommendations, 1):
                st.text(f"{i}. {rec}")
        
        # Critical issues
        if analysis_result.critical_issues:
            st.subheader("⚠️ Critical Issues")
            for issue in analysis_result.critical_issues:
                st.error(issue)
        
        # Download options
        st.subheader("💾 Download Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Download JSON"):
                report_json = json.dumps(analysis_result.report.__dict__, indent=2, default=str)
                st.download_button(
                    label="Download as JSON",
                    data=report_json,
                    file_name=f"{report.project_name}_analysis.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📊 Download CSV"):
                room_data = []
                for room in report.rooms:
                    room_data.append({
                        "room_name": room.name,
                        "room_type": room.room_type.value,
                        "area": room.area,
                        "illuminance_avg": room.illuminance_avg,
                        "uniformity": room.uniformity,
                        "ugr": room.ugr,
                        "power_density": room.power_density,
                        "data_completeness": room.data_completeness,
                        "confidence_score": room.confidence_score
                    })
                
                csv_data = pd.DataFrame(room_data).to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name=f"{report.project_name}_rooms.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📋 Download Report"):
                report_text = f"""
DIALUX ANALYSIS REPORT
=====================
Project: {report.project_name}
Analysis Date: {report.processing_date}
Total Rooms: {report.total_rooms}
Total Area: {report.total_area:.1f} m²
Overall Compliance: {report.overall_compliance_rate:.1%}
Data Quality: {report.data_quality_score:.1%}

ROOM DETAILS:
"""
                for room in report.rooms:
                    report_text += f"\n{room.name} ({room.room_type.value}):\n"
                    report_text += f"  Area: {room.area:.1f} m²\n"
                    if room.illuminance_avg:
                        report_text += f"  Illuminance: {room.illuminance_avg:.0f} lux\n"
                    if room.uniformity:
                        report_text += f"  Uniformity: {room.uniformity:.2f}\n"
                    if room.ugr:
                        report_text += f"  UGR: {room.ugr:.1f}\n"
                    if room.power_density:
                        report_text += f"  Power Density: {room.power_density:.1f} W/m²\n"
                
                if analysis_result.recommendations:
                    report_text += "\nRECOMMENDATIONS:\n"
                    for i, rec in enumerate(analysis_result.recommendations, 1):
                        report_text += f"{i}. {rec}\n"
                
                st.download_button(
                    label="Download as TXT",
                    data=report_text,
                    file_name=f"{report.project_name}_report.txt",
                    mime="text/plain"
                )
    
    def _display_comparison_results(self, comparisons, standard_a, standard_b, room_type):
        """Display standards comparison results"""
        st.subheader("⚖️ Standards Comparison Results")
        
        if not comparisons:
            st.warning("No comparable parameters found between the selected standards")
            return
        
        st.text(f"Comparing {standard_a} vs {standard_b} for {room_type}")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Comparable Parameters", len(comparisons))
        
        with col2:
            more_strict_a = sum(1 for c in comparisons if c.more_strict.value == standard_a)
            st.metric(f"{standard_a} More Strict", more_strict_a)
        
        with col3:
            more_strict_b = sum(1 for c in comparisons if c.more_strict.value == standard_b)
            st.metric(f"{standard_b} More Strict", more_strict_b)
        
        # Comparison table
        st.subheader("📊 Detailed Comparison")
        comparison_data = []
        for comp in comparisons:
            comparison_data.append({
                "Parameter": comp.parameter,
                f"{standard_a}": comp.value_a,
                f"{standard_b}": comp.value_b,
                "Difference": comp.difference,
                "Difference %": f"{comp.difference_percentage:.1f}%",
                "More Strict": comp.more_strict.value,
                "Recommendation": comp.harmonization_recommendation
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Visualization
        if len(comparisons) > 0:
            st.subheader("📈 Comparison Visualization")
            
            param_names = [comp.parameter for comp in comparisons]
            values_a = [comp.value_a for comp in comparisons]
            values_b = [comp.value_b for comp in comparisons]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name=standard_a, x=param_names, y=values_a))
            fig.add_trace(go.Bar(name=standard_b, x=param_names, y=values_b))
            
            fig.update_layout(
                title="Parameter Comparison",
                xaxis_title="Parameter",
                yaxis_title="Value",
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Download options
        st.subheader("💾 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Comparison"):
                comparison_json = json.dumps([comp.__dict__ for comp in comparisons], indent=2, default=str)
                st.download_button(
                    label="Download as JSON",
                    data=comparison_json,
                    file_name=f"comparison_{standard_a}_{standard_b}_{room_type}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📄 Download CSV"):
                csv_data = comparison_df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name=f"comparison_{standard_a}_{standard_b}_{room_type}.csv",
                    mime="text/csv"
                )

def main():
    """Main function to run the web interface"""
    interface = UnifiedWebInterface()
    interface.run()

if __name__ == "__main__":
    main()
