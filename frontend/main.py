import streamlit as st
import requests
import json
from typing import Optional

# Configuración de la página
st.set_page_config(
    page_title="Scientific Paper Classifier",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE_URL = "http://localhost:8000"  # Cambia por tu URL de FastAPI
CLASSIFY_ENDPOINT = f"{API_BASE_URL}/classify/"

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .category-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid;
    }
    .cardiovascular {
        background-color: #ffebee;
        border-left-color: #e91e63;
    }
    .neurological {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    .hepatorenal {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .oncological {
        background-color: #fce4ec;
        border-left-color: #9c27b0;
    }
    .confidence-high {
        color: #4caf50;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ff9800;
        font-weight: bold;
    }
    .confidence-low {
        color: #f44336;
        font-weight: bold;
    }
    .result-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_confidence_class(confidence: float) -> str:
    """Retorna la clase CSS basada en el nivel de confianza"""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.6:
        return "confidence-medium"
    else:
        return "confidence-low"

def get_confidence_text(confidence: float) -> str:
    """Returns the descriptive text for confidence level"""
    if confidence >= 0.8:
        return "High"
    elif confidence >= 0.6:
        return "Medium"
    else:
        return "Low"

def classify_paper(title: str, abstract: str) -> Optional[dict]:
    """Calls the API to classify the paper"""
    try:
        payload = {
            "title": title,
            "abstract": abstract
        }
        
        with st.spinner("🔍 Classifying the scientific paper..."):
            response = requests.post(
                CLASSIFY_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # 60 seconds timeout
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error decoding response: {str(e)}")
        return None

def display_result(result: dict):
    """Displays the classification results"""
    category = result.get("category", "")
    confidence = result.get("confidence", 0.0)
    rationale = result.get("rationale", "")
    
    # Category mapping to colors and emojis
    category_info = {
        "Cardiovascular": {"emoji": "❤️", "color": "cardiovascular"},
        "Neurological": {"emoji": "🧠", "color": "neurological"},
        "Hepatorenal": {"emoji": "🫀", "color": "hepatorenal"},
        "Oncological": {"emoji": "🎗️", "color": "oncological"}
    }
    
    info = category_info.get(category, {"emoji": "🔬", "color": "cardiovascular"})
    
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    
    # Result title
    st.markdown(f"### 🎯 Classification Result")
    
    # Create columns to display information
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="category-card {info['color']}">
            <h4 style="color: #2d3748; margin: 0;">{info['emoji']} {category}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        confidence_class = get_confidence_class(confidence)
        confidence_text = get_confidence_text(confidence)
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h5>Confidence</h5>
            <span class="{confidence_class}">{confidence:.1%}</span><br>
            <small>({confidence_text})</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Visual confidence meter
        st.metric(
            label="Score",
            value=f"{confidence:.3f}",
            delta=f"{confidence_text} confidence"
        )
    
    # Rationale
    st.markdown("### 💭 Rationale")
    st.markdown(f"""
    <div style="background-color: #f7fafc; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #4299e1; border: 1px solid #e2e8f0;">
        <p style="margin: 0; line-height: 1.6; color: #2d3748; font-size: 16px;">{rationale}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Main title
    st.markdown('<h1 class="main-header">🔬 Scientific Paper Classifier</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Description
    st.markdown("""
    This application uses artificial intelligence to classify scientific papers into one of the following categories:
    - **❤️ Cardiovascular**: Related to the cardiovascular system
    - **🧠 Neurological**: Related to the neurological system
    - **🫀 Hepatorenal**: Related to the hepatorenal system
    - **🎗️ Oncological**: Related to oncology
    """)
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### ℹ️ Information")
        st.markdown("""
        **How to use:**
        1. Enter the paper title
        2. Paste the complete abstract
        3. Click 'Classify Paper'
        4. Review the results
        """)
        
        st.markdown("### 📊 Confidence Metrics")
        st.markdown("""
        - **High** (≥80%): Very reliable
        - **Medium** (60-79%): Moderately reliable  
        - **Low** (<60%): Review manually
        """)
        
        # API status
        st.markdown("### 🔌 API Status")
        try:
            health_response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if health_response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.error("❌ API Issues")
        except:
            st.error("❌ API Disconnected")
    
    # Main form
    with st.form("paper_form", clear_on_submit=False):
        st.markdown("### 📝 Paper Information")
        
        # Title field
        title = st.text_input(
            "Paper Title",
            placeholder="Enter the complete title of the scientific paper...",
            help="The title should be descriptive and specific"
        )
        
        # Abstract field
        abstract = st.text_area(
            "Abstract",
            placeholder="Paste the complete abstract of the paper here...",
            height=200,
            help="The abstract should include objectives, methods, results, and conclusions"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Classify Paper",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validations
            if not title.strip():
                st.error("⚠️ Please enter the paper title")
                return
            
            if not abstract.strip():
                st.error("⚠️ Please enter the paper abstract")
                return
                
            if len(abstract.strip()) < 50:
                st.warning("⚠️ The abstract seems very short. Are you sure it's complete?")
            
            # Call API
            result = classify_paper(title.strip(), abstract.strip())
            
            if result:
                st.success("✅ Paper classified successfully!")
                display_result(result)
            else:
                st.error("❌ Could not classify the paper. Please try again.")
    
    # Button to classify another paper (outside the form)
    if st.session_state.get('show_results', False):
        if st.button("🔄 Classify another paper", key="reset_button"):
            # Clear the session state to reset the form
            st.session_state['show_results'] = False
            st.rerun()

    # Examples
    with st.expander("📚 View paper examples"):
        st.markdown("### Examples by category:")
        
        examples = {
            "Cardiovascular": {
                "title": "Effects of ACE inhibitors on cardiovascular outcomes in patients with heart failure",
                "abstract": "Background: Heart failure remains a leading cause of morbidity and mortality worldwide. ACE inhibitors have shown promise in improving cardiovascular outcomes. Methods: We conducted a randomized controlled trial involving 2000 patients with heart failure. Results: ACE inhibitors significantly reduced cardiovascular mortality by 25% and hospitalization rates by 30%. Conclusions: ACE inhibitors provide substantial cardiovascular benefits in heart failure patients."
            },
            "Neurological": {
                "title": "Deep brain stimulation for treatment-resistant depression: a systematic review",
                "abstract": "Background: Treatment-resistant depression affects millions worldwide, with limited therapeutic options. Deep brain stimulation (DBS) has emerged as a potential intervention. Methods: We systematically reviewed studies of DBS in treatment-resistant depression. Results: DBS showed significant improvement in depression scores in 60% of patients, with sustained effects over 12 months. Conclusions: DBS represents a promising therapeutic option for treatment-resistant depression."
            }
        }
        
        for category, example in examples.items():
            st.markdown(f"**{category}:**")
            st.markdown(f"*Title:* {example['title']}")
            st.markdown(f"*Abstract:* {example['abstract']}")
            st.markdown("---")

if __name__ == "__main__":
    main()