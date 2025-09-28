#!/usr/bin/env python3
"""
Web Interface Entry Point for Unified Lighting Analyzer
"""
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now import and run the web interface
if __name__ == "__main__":
    import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import json
    import tempfile
    import shutil
    from typing import Dict, List, Any, Optional
    import logging

    # Import our modules with absolute imports
    from core.config import config
    from extractors.pdf_extractor import PDFExtractor
    from extractors.table_extractor import AdvancedTableExtractor
    from standards.standards_processor import StandardsProcessor, StandardType, RoomType
    from analyzers.dialux_analyzer import DialuxAnalyzer
    from analyzers.fast_dialux_analyzer import FastDialuxAnalyzer

    logger = logging.getLogger(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Page configuration
    st.set_page_config(
        page_title="Unified Lighting Analyzer",
        page_icon="💡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    def main():
        """Main web interface"""
        st.markdown('<h1 class="main-header">💡 Unified Lighting Analyzer</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox(
            "Choose a feature:",
            ["🏠 Home", "📄 PDF Extraction", "📊 Table Analysis", "🏢 Dialux Analysis", "📋 Standards", "⚙️ Settings"]
        )

        if page == "🏠 Home":
            show_home_page()
        elif page == "📄 PDF Extraction":
            show_pdf_extraction_page()
        elif page == "📊 Table Analysis":
            show_table_analysis_page()
        elif page == "🏢 Dialux Analysis":
            show_dialux_analysis_page()
        elif page == "📋 Standards":
            show_standards_page()
        elif page == "⚙️ Settings":
            show_settings_page()

    def show_home_page():
        """Home page with overview"""
        st.markdown("""
        ## Welcome to the Unified Lighting Analyzer! 🎉

        This powerful tool combines the best features from all your lighting analysis projects:

        ### 🔧 **Core Features:**
        - **Multi-method PDF extraction** (pdfplumber, PyMuPDF, pdfminer, OCR)
        - **Advanced table extraction** with quality analysis
        - **⚡ Fast Dialux analysis** with area extraction and company details
        - **🤖 Enhanced Dialux analysis** with OpenAI for comprehensive extraction
        - **Standards compliance checking** (EN 12464-1, BREEAM)
        - **Interactive web interface** with real-time results

        ### 📊 **What You Can Analyze:**
        - **Illuminance levels** and uniformity ratios
        - **UGR (glare rating)** and power density
        - **Color temperature** and CRI values
        - **Room-by-room compliance** against lighting standards
        - **Specific recommendations** for improvements

        ### 🚀 **Getting Started:**
        1. Upload your PDF file using the navigation menu
        2. Choose the analysis type:
           - **⚡ Fast Analysis**: Quick results with area extraction (Recommended)
           - **🤖 Enhanced Analysis**: Comprehensive extraction with OpenAI
           - **🔍 Standard Analysis**: Traditional analysis method
        3. View results with interactive charts and detailed reports
        4. Export results in multiple formats (JSON, CSV, Excel, PDF)

        ---
        """)

        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Supported Standards", "2", "EN 12464-1, BREEAM")
        
        with col2:
            st.metric("Extraction Methods", "4", "pdfplumber, PyMuPDF, pdfminer, OCR")
        
        with col3:
            st.metric("Output Formats", "4", "JSON, CSV, Excel, PDF")
        
        with col4:
            st.metric("Room Types", "5+", "Office, Meeting, Corridor, Storage, Industrial")

    def show_pdf_extraction_page():
        """PDF extraction page"""
        st.header("📄 PDF Text & Data Extraction")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload any PDF file for text and data extraction"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                shutil.copyfileobj(uploaded_file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                with st.spinner("Extracting text and data from PDF..."):
                    extractor = PDFExtractor()
                    result = extractor.extract_from_pdf(tmp_path)
                
                st.success("✅ PDF extraction completed!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📝 Extracted Text")
                    st.text_area("Text content:", result.text, height=200)
                
                with col2:
                    st.subheader("📊 Metadata")
                    st.json(result.metadata)
                
                # Display tables if any
                if result.tables:
                    st.subheader("📋 Extracted Tables")
                    for i, table in enumerate(result.tables):
                        st.write(f"**Table {i+1}:**")
                        st.dataframe(table)
                
                # Display extraction info
                st.info(f"""
                **Extraction Summary:**
                - Method: {result.extraction_method}
                - Confidence: {result.confidence_score:.1%}
                - Processing time: {result.processing_time:.2f}s
                - Tables found: {len(result.tables)}
                - Text length: {len(result.text)} characters
                """)
                
            except Exception as e:
                st.error(f"❌ Extraction failed: {str(e)}")
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)

    def show_table_analysis_page():
        """Table analysis page"""
        st.header("📊 Advanced Table Analysis")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file for table analysis",
            type=['pdf'],
            help="Upload a PDF file to extract and analyze tables"
        )
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                shutil.copyfileobj(uploaded_file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                with st.spinner("Analyzing tables in PDF..."):
                    extractor = AdvancedTableExtractor()
                    tables = extractor.extract_tables(tmp_path)
                
                st.success(f"✅ Found {len(tables)} high-quality tables!")
                
                for i, table in enumerate(tables):
                    st.subheader(f"📋 Table {i+1}")
                    st.dataframe(table)
                    
                    # Table statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(table))
                    with col2:
                        st.metric("Columns", len(table.columns))
                    with col3:
                        st.metric("Cells", len(table) * len(table.columns))
                
            except Exception as e:
                st.error(f"❌ Table analysis failed: {str(e)}")
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    def show_dialux_analysis_page():
        """Dialux analysis page"""
        st.header("🏢 Dialux Report Analysis")
        
        # Analysis method selection
        analysis_method = st.selectbox(
            "Choose analysis method:",
            ["⚡ Fast Analysis (Recommended)", "🔍 Standard Analysis", "🤖 Enhanced Analysis (OpenAI)"],
            help="Fast analysis is recommended for quick results with area extraction"
        )
        
        # API key input for enhanced analysis
        api_key = None
        if "Enhanced" in analysis_method:
            api_key = st.text_input(
                "OpenAI API Key:",
                type="password",
                help="Enter your OpenAI API key for enhanced analysis"
            )
            if not api_key:
                st.warning("⚠️ OpenAI API key is required for enhanced analysis")
                return
        elif "Fast" in analysis_method:
            api_key = st.text_input(
                "OpenAI API Key (Optional):",
                type="password",
                help="Optional: Enter your OpenAI API key for better company name extraction"
            )
        
        uploaded_file = st.file_uploader(
            "Choose a Dialux report PDF",
            type=['pdf'],
            help="Upload a Dialux report for comprehensive analysis"
        )
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                shutil.copyfileobj(uploaded_file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                if "Fast" in analysis_method:
                    with st.spinner("⚡ Fast analysis in progress..."):
                        analyzer = FastDialuxAnalyzer(api_key)
                        result = analyzer.analyze_dialux_report(tmp_path)
                elif "Enhanced" in analysis_method:
                    with st.spinner("🤖 Enhanced analysis with OpenAI..."):
                        from analyzers.enhanced_dialux_analyzer import EnhancedDialuxAnalyzer
                        analyzer = EnhancedDialuxAnalyzer(api_key)
                        result = analyzer.analyze_dialux_report(tmp_path)
                else:
                    with st.spinner("🔍 Standard analysis in progress..."):
                        analyzer = DialuxAnalyzer()
                        result = analyzer.analyze_dialux_report(tmp_path)
                
                # Show processing time
                if hasattr(result, 'processing_time'):
                    st.success(f"✅ Analysis completed in {result.processing_time:.2f}s!")
                else:
                    st.success("✅ Analysis completed!")
                
                report = result.report
                
                # ===== COMPREHENSIVE PROJECT OVERVIEW =====
                st.header("📊 COMPREHENSIVE DIALUX ANALYSIS REPORT")
                st.markdown("---")
                
                # Project Information Section
                st.subheader("🏢 PROJECT INFORMATION")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Basic Information:**")
                    st.write(f"• **Project Name:** {report.project_name or 'Not specified'}")
                    st.write(f"• **Total Rooms:** {report.total_rooms}")
                    st.write(f"• **Total Area:** {report.total_area:.1f} m²")
                    st.write(f"• **Overall Compliance:** {report.overall_compliance_rate:.1%}")
                    if hasattr(report, 'data_quality_score'):
                        st.write(f"• **Data Quality Score:** {report.data_quality_score:.1%}")
                
                with col2:
                    st.write("**Company Information:**")
                    if hasattr(report, 'project_company') and report.project_company:
                        st.write(f"• **Project Company:** {report.project_company}")
                    if hasattr(report, 'luminaire_manufacturer') and report.luminaire_manufacturer:
                        st.write(f"• **Luminaire Manufacturer:** {report.luminaire_manufacturer}")
                    if hasattr(report, 'driver_circuit_company') and report.driver_circuit_company:
                        st.write(f"• **Driver Circuit Company:** {report.driver_circuit_company}")
                    if hasattr(report, 'consultant_company') and report.consultant_company:
                        st.write(f"• **Consultant:** {report.consultant_company}")
                    if hasattr(report, 'installer_company') and report.installer_company:
                        st.write(f"• **Installer:** {report.installer_company}")
                
                # ===== DETAILED ROOM ANALYSIS =====
                if report.rooms:
                    st.subheader("🏠 DETAILED ROOM ANALYSIS")
                    
                    for i, room in enumerate(report.rooms, 1):
                        # Handle different room types (string vs enum)
                        room_type = room.room_type
                        if hasattr(room_type, 'value'):
                            room_type = room_type.value
                        elif hasattr(room_type, 'name'):
                            room_type = room_type.name
                        
                        with st.expander(f"📋 Room {i}: {room.name} ({room_type})", expanded=True):
                            # Room Basic Information
                            st.write("**📐 Room Specifications:**")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Area", f"{room.area:.1f} m²")
                                if hasattr(room, 'illuminance_avg') and room.illuminance_avg:
                                    st.metric("Avg Illuminance", f"{room.illuminance_avg:.0f} lux")
                            
                            with col2:
                                if hasattr(room, 'uniformity') and room.uniformity:
                                    st.metric("Uniformity", f"{room.uniformity:.2f}")
                                if hasattr(room, 'ugr') and room.ugr:
                                    st.metric("UGR", f"{room.ugr:.1f}")
                            
                            with col3:
                                if hasattr(room, 'power_density') and room.power_density:
                                    st.metric("Power Density", f"{room.power_density:.1f} W/m²")
                                if hasattr(room, 'luminaire_count') and room.luminaire_count:
                                    st.metric("Luminaires", f"{room.luminaire_count}")
                            
                            # Detailed Lighting Parameters
                            st.write("**💡 Detailed Lighting Parameters:**")
                            param_col1, param_col2 = st.columns(2)
                            
                            with param_col1:
                                if hasattr(room, 'illuminance_min') and room.illuminance_min:
                                    st.write(f"• **Min Illuminance:** {room.illuminance_min:.0f} lux")
                                if hasattr(room, 'illuminance_max') and room.illuminance_max:
                                    st.write(f"• **Max Illuminance:** {room.illuminance_max:.0f} lux")
                                if hasattr(room, 'color_temperature') and room.color_temperature:
                                    st.write(f"• **Color Temperature:** {room.color_temperature:.0f} K")
                            
                            with param_col2:
                                if hasattr(room, 'cri') and room.cri:
                                    st.write(f"• **CRI:** {room.cri}")
                                if hasattr(room, 'luminaire_spacing') and room.luminaire_spacing:
                                    st.write(f"• **Luminaire Spacing:** {room.luminaire_spacing:.1f} m")
                                if hasattr(room, 'mounting_height') and room.mounting_height:
                                    st.write(f"• **Mounting Height:** {room.mounting_height:.1f} m")
                            
                            # ===== COMPREHENSIVE STANDARDS COMPARISON =====
                            if hasattr(room, 'compliance_results') and room.compliance_results:
                                st.write("**📋 COMPREHENSIVE STANDARDS COMPARISON:**")
                                
                                # Group compliance results by standard
                                standards_dict = {}
                                for comp in room.compliance_results:
                                    if comp.standard not in standards_dict:
                                        standards_dict[comp.standard] = []
                                    standards_dict[comp.standard].append(comp)
                                
                                # Display each standard's requirements
                                for standard_name, comp_results in standards_dict.items():
                                    st.write(f"**{standard_name} Standard Requirements:**")
                                    
                                    # Create a detailed comparison table
                                    comparison_data = []
                                    for comp in comp_results:
                                        status_icon = "✅" if comp.is_compliant else "❌"
                                        deviation = comp.deviation if hasattr(comp, 'deviation') else 0
                                        
                                        comparison_data.append({
                                            "Parameter": comp.parameter.title(),
                                            "Status": status_icon,
                                            "Actual Value": f"{comp.actual_value} {comp.unit}",
                                            "Required Value": f"{comp.required_value} {comp.unit}",
                                            "Deviation": f"{deviation:+.1f} {comp.unit}",
                                            "Compliant": "Yes" if comp.is_compliant else "No"
                                        })
                                    
                                    if comparison_data:
                                        import pandas as pd
                                        df = pd.DataFrame(comparison_data)
                                        st.dataframe(df, use_container_width=True)
                                    
                                    # Summary for this standard
                                    compliant_count = sum(1 for comp in comp_results if comp.is_compliant)
                                    total_count = len(comp_results)
                                    compliance_rate = (compliant_count / total_count) * 100 if total_count > 0 else 0
                                    
                                    if compliance_rate >= 80:
                                        st.success(f"✅ {standard_name}: {compliant_count}/{total_count} parameters compliant ({compliance_rate:.1f}%)")
                                    elif compliance_rate >= 60:
                                        st.warning(f"⚠️ {standard_name}: {compliant_count}/{total_count} parameters compliant ({compliance_rate:.1f}%)")
                                    else:
                                        st.error(f"❌ {standard_name}: {compliant_count}/{total_count} parameters compliant ({compliance_rate:.1f}%)")
                                
                                st.markdown("---")
                
                # ===== COMPREHENSIVE RECOMMENDATIONS =====
                if result.recommendations:
                    st.subheader("💡 COMPREHENSIVE RECOMMENDATIONS")
                    
                    # Categorize recommendations
                    illuminance_recs = [rec for rec in result.recommendations if 'illuminance' in rec.lower()]
                    uniformity_recs = [rec for rec in result.recommendations if 'uniformity' in rec.lower()]
                    glare_recs = [rec for rec in result.recommendations if 'glare' in rec.lower() or 'ugr' in rec.lower()]
                    power_recs = [rec for rec in result.recommendations if 'power' in rec.lower()]
                    general_recs = [rec for rec in result.recommendations if not any(keyword in rec.lower() for keyword in ['illuminance', 'uniformity', 'glare', 'ugr', 'power'])]
                    
                    rec_col1, rec_col2 = st.columns(2)
                    
                    with rec_col1:
                        if illuminance_recs:
                            st.write("**🔆 Illuminance Recommendations:**")
                            for i, rec in enumerate(illuminance_recs, 1):
                                st.write(f"{i}. {rec}")
                        
                        if uniformity_recs:
                            st.write("**📐 Uniformity Recommendations:**")
                            for i, rec in enumerate(uniformity_recs, 1):
                                st.write(f"{i}. {rec}")
                    
                    with rec_col2:
                        if glare_recs:
                            st.write("**👁️ Glare Control Recommendations:**")
                            for i, rec in enumerate(glare_recs, 1):
                                st.write(f"{i}. {rec}")
                        
                        if power_recs:
                            st.write("**⚡ Power Efficiency Recommendations:**")
                            for i, rec in enumerate(power_recs, 1):
                                st.write(f"{i}. {rec}")
                    
                    if general_recs:
                        st.write("**📋 General Recommendations:**")
                        for i, rec in enumerate(general_recs, 1):
                            st.write(f"{i}. {rec}")
                
                # ===== CRITICAL ISSUES =====
                if result.critical_issues:
                    st.subheader("⚠️ CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION")
                    for i, issue in enumerate(result.critical_issues, 1):
                        st.error(f"🚨 **Critical Issue {i}:** {issue}")
                
                # ===== SUMMARY STATISTICS =====
                st.subheader("📊 ANALYSIS SUMMARY")
                summary_col1, summary_col2, summary_col3 = st.columns(3)
                
                with summary_col1:
                    st.metric("Total Rooms Analyzed", report.total_rooms)
                    st.metric("Total Project Area", f"{report.total_area:.1f} m²")
                
                with summary_col2:
                    st.metric("Overall Compliance Rate", f"{report.overall_compliance_rate:.1%}")
                    if hasattr(report, 'data_quality_score'):
                        st.metric("Data Quality Score", f"{report.data_quality_score:.1%}")
                
                with summary_col3:
                    if result.recommendations:
                        st.metric("Total Recommendations", len(result.recommendations))
                    if result.critical_issues:
                        st.metric("Critical Issues", len(result.critical_issues))
                
                # ===== EXPORT OPTIONS =====
                st.subheader("💾 EXPORT ANALYSIS RESULTS")
                export_col1, export_col2, export_col3 = st.columns(3)
                
                with export_col1:
                    if st.button("📄 Export as PDF Report"):
                        st.info("PDF export functionality will be implemented")
                
                with export_col2:
                    if st.button("📊 Export as Excel"):
                        st.info("Excel export functionality will be implemented")
                
                with export_col3:
                    if st.button("📋 Export as JSON"):
                        st.info("JSON export functionality will be implemented")
                
            except Exception as e:
                st.error(f"❌ Dialux analysis failed: {str(e)}")
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    def show_standards_page():
        """Standards information page"""
        st.header("📋 Lighting Standards")
        
        try:
            processor = StandardsProcessor()
            standards = processor.get_available_standards()
            
            st.subheader("Available Standards")
            
            for standard_name, standard_info in standards.items():
                with st.expander(f"📄 {standard_info['name']} (v{standard_info['version']})"):
                    st.write(f"**Description:** {standard_info.get('description', 'No description available')}")
                    
                    if 'requirements' in standard_info:
                        st.write("**Room Requirements:**")
                        for room_type, requirements in standard_info['requirements'].items():
                            st.write(f"**{room_type.replace('_', ' ').title()}:**")
                            for param, value in requirements.items():
                                if isinstance(value, (int, float)):
                                    st.write(f"  • {param.replace('_', ' ').title()}: {value}")
                                else:
                                    st.write(f"  • {param.replace('_', ' ').title()}: {value}")
        
        except Exception as e:
            st.error(f"❌ Failed to load standards: {str(e)}")

    def show_settings_page():
        """Settings page"""
        st.header("⚙️ Settings")
        
        st.subheader("Configuration")
        st.info("Current configuration settings are loaded from the system defaults.")
        
        st.subheader("About")
        st.write("""
        **Unified Lighting Analyzer v1.0**
        
        This tool combines the best features from multiple lighting analysis projects:
        - Basic PDF extraction capabilities
        - Advanced table extraction with quality analysis
        - Intelligent Dialux report processing
        - Standards compliance checking
        
        Built with Python, Streamlit, and advanced PDF processing libraries.
        """)

    # Run the main function
    if __name__ == "__main__":
        main()
