"""
Demo Generation Pipeline for Business Intelligence

Automated proof-of-concept generation system that:
- Analyzes company data and automation opportunities
- Generates functional code demonstrations
- Creates professional presentation materials
- Deploys demos to staging environments
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func
from jinja2 import Environment, FileSystemLoader

from app.models.business_intelligence import Company, Opportunity, Demo
from app.core.database import get_db


class DemoGenerator:
    """
    Automated demo generation system for business opportunities
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.demo_base_path = Path("storage/demos")
        self.template_path = Path("app/templates/demos")
        self.staging_url_base = "https://demos.jobbot.ai"
        
        # Ensure directories exist
        self.demo_base_path.mkdir(parents=True, exist_ok=True)
        self.template_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_path)),
            autoescape=True
        )
    
    async def generate_demo(self, opportunity_id: int, demo_config: Dict[str, Any]) -> Demo:
        """
        Generate a complete demo for a business opportunity
        """
        # Get opportunity and company data
        opportunity = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            raise ValueError(f"Opportunity {opportunity_id} not found")
        
        company = opportunity.company
        
        # Create demo record
        demo = Demo(
            company_id=company.id,
            opportunity_id=opportunity.id,
            title=f"{opportunity.title} - Proof of Concept",
            description=f"Automated demo showcasing {opportunity.title} for {company.name}",
            demo_type=demo_config.get("type", "web_app"),
            status="development",
            technologies_used=demo_config.get("technologies", []),
            features_demonstrated=demo_config.get("features", [])
        )
        
        self.db.add(demo)
        self.db.commit()
        self.db.refresh(demo)
        
        try:
            # Generate demo based on type
            if demo.demo_type == "web_app":
                await self._generate_web_app_demo(demo, opportunity, company, demo_config)
            elif demo.demo_type == "automation_script":
                await self._generate_automation_demo(demo, opportunity, company, demo_config)
            elif demo.demo_type == "dashboard":
                await self._generate_dashboard_demo(demo, opportunity, company, demo_config)
            elif demo.demo_type == "api_integration":
                await self._generate_api_demo(demo, opportunity, company, demo_config)
            else:
                raise ValueError(f"Unsupported demo type: {demo.demo_type}")
            
            # Generate presentation materials
            await self._generate_presentation_materials(demo, opportunity, company)
            
            # Deploy to staging
            await self._deploy_demo(demo)
            
            # Update demo status
            demo.status = "ready"
            demo.completion_percentage = 100.0
            self.db.commit()
            
            return demo
            
        except Exception as e:
            demo.status = "failed"
            demo.client_feedback = f"Generation failed: {str(e)}"
            self.db.commit()
            raise
    
    async def _generate_web_app_demo(self, demo: Demo, opportunity: Opportunity, company: Company, config: Dict[str, Any]):
        """
        Generate a web application demo
        """
        demo_id = str(demo.id)
        demo_path = self.demo_base_path / demo_id
        demo_path.mkdir(exist_ok=True)
        
        # Determine demo template based on opportunity category
        if opportunity.category == "data_processing":
            template_name = "data_dashboard"
        elif opportunity.category == "workflow_automation":
            template_name = "workflow_app"
        elif opportunity.category == "reporting":
            template_name = "analytics_dashboard"
        else:
            template_name = "generic_webapp"
        
        # Prepare template context
        context = {
            "company": {
                "name": company.name,
                "industry": company.industry,
                "description": company.description
            },
            "opportunity": {
                "title": opportunity.title,
                "description": opportunity.description,
                "category": opportunity.category,
                "estimated_value": opportunity.estimated_value
            },
            "demo": {
                "id": demo_id,
                "title": demo.title,
                "features": demo.features_demonstrated
            },
            "sample_data": await self._generate_sample_data(company, opportunity),
            "branding": {
                "primary_color": config.get("primary_color", "#3B82F6"),
                "secondary_color": config.get("secondary_color", "#10B981"),
                "logo_url": config.get("logo_url", "/assets/default-logo.png")
            }
        }
        
        # Generate React application
        await self._create_react_app(demo_path, template_name, context)
        
        # Update demo with file paths
        demo.demo_files_path = str(demo_path)
        demo.demo_code_repository = f"https://github.com/jobbot-demos/{demo_id}"
        
        # Calculate development metrics
        demo.development_hours = config.get("estimated_hours", 8.0)
        demo.development_cost = demo.development_hours * 150  # $150/hour rate
    
    async def _generate_automation_demo(self, demo: Demo, opportunity: Opportunity, company: Company, config: Dict[str, Any]):
        """
        Generate an automation script demo
        """
        demo_id = str(demo.id)
        demo_path = self.demo_base_path / demo_id
        demo_path.mkdir(exist_ok=True)
        
        # Create Python automation script
        script_content = await self._generate_automation_script(company, opportunity, config)
        
        script_file = demo_path / "automation_demo.py"
        with open(script_file, "w") as f:
            f.write(script_content)
        
        # Create requirements.txt
        requirements = [
            "pandas>=2.0.0",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
            "openpyxl>=3.0.0",
            "python-dotenv>=1.0.0"
        ]
        
        with open(demo_path / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        # Create README with usage instructions
        readme_content = await self._generate_automation_readme(demo, opportunity, company)
        with open(demo_path / "README.md", "w") as f:
            f.write(readme_content)
        
        # Update demo record
        demo.demo_files_path = str(demo_path)
        demo.technologies_used = ["Python", "Pandas", "Automation"]
        demo.development_hours = 4.0
        demo.development_cost = 600.0
    
    async def _generate_dashboard_demo(self, demo: Demo, opportunity: Opportunity, company: Company, config: Dict[str, Any]):
        """
        Generate a business intelligence dashboard demo
        """
        demo_id = str(demo.id)
        demo_path = self.demo_base_path / demo_id
        demo_path.mkdir(exist_ok=True)
        
        # Create Streamlit dashboard
        dashboard_content = await self._generate_streamlit_dashboard(company, opportunity, config)
        
        with open(demo_path / "dashboard.py", "w") as f:
            f.write(dashboard_content)
        
        # Generate sample data files
        sample_data = await self._generate_sample_data(company, opportunity)
        
        for data_name, data_content in sample_data.items():
            if isinstance(data_content, list):
                import pandas as pd
                df = pd.DataFrame(data_content)
                df.to_csv(demo_path / f"{data_name}.csv", index=False)
        
        # Create requirements.txt for Streamlit
        requirements = [
            "streamlit>=1.28.0",
            "pandas>=2.0.0",
            "plotly>=5.15.0",
            "altair>=5.0.0"
        ]
        
        with open(demo_path / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        demo.demo_files_path = str(demo_path)
        demo.technologies_used = ["Python", "Streamlit", "Plotly", "Pandas"]
        demo.development_hours = 6.0
        demo.development_cost = 900.0
    
    async def _create_react_app(self, demo_path: Path, template_name: str, context: Dict[str, Any]):
        """
        Create a React application from template
        """
        # Create package.json
        package_json = {
            "name": f"demo-{context['demo']['id']}",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "recharts": "^2.8.0",
                "lucide-react": "^0.294.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(demo_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create React component based on template
        component_content = await self._render_template(f"{template_name}.jsx", context)
        
        src_path = demo_path / "src"
        src_path.mkdir(exist_ok=True)
        
        with open(src_path / "App.js", "w") as f:
            f.write(component_content)
        
        # Create index.html
        html_content = await self._render_template("index.html", context)
        public_path = demo_path / "public"
        public_path.mkdir(exist_ok=True)
        
        with open(public_path / "index.html", "w") as f:
            f.write(html_content)
    
    async def _generate_sample_data(self, company: Company, opportunity: Opportunity) -> Dict[str, Any]:
        """
        Generate realistic sample data for the demo
        """
        if opportunity.category == "data_processing":
            return {
                "sales_data": [
                    {"month": "Jan", "revenue": 45000, "customers": 120},
                    {"month": "Feb", "revenue": 52000, "customers": 135},
                    {"month": "Mar", "revenue": 48000, "customers": 128},
                    {"month": "Apr", "revenue": 61000, "customers": 155},
                    {"month": "May", "revenue": 58000, "customers": 148},
                    {"month": "Jun", "revenue": 67000, "customers": 172}
                ],
                "efficiency_metrics": [
                    {"process": "Order Processing", "before": 45, "after": 12, "improvement": 73},
                    {"process": "Invoice Generation", "before": 30, "after": 5, "improvement": 83},
                    {"process": "Customer Onboarding", "before": 120, "after": 25, "improvement": 79}
                ]
            }
        elif opportunity.category == "workflow_automation":
            return {
                "workflow_steps": [
                    {"step": "Data Entry", "current_time": 120, "automated_time": 5, "frequency": "Daily"},
                    {"step": "Report Generation", "current_time": 240, "automated_time": 15, "frequency": "Weekly"},
                    {"step": "Email Notifications", "current_time": 60, "automated_time": 2, "frequency": "Daily"}
                ],
                "cost_savings": {
                    "annual_labor_cost": 45000,
                    "automation_savings": 38250,
                    "roi_percentage": 85
                }
            }
        else:
            return {
                "generic_metrics": [
                    {"metric": "Efficiency", "value": 85, "target": 90},
                    {"metric": "Cost Reduction", "value": 35, "target": 50},
                    {"metric": "Time Savings", "value": 60, "target": 75}
                ]
            }
    
    async def _generate_presentation_materials(self, demo: Demo, opportunity: Opportunity, company: Company):
        """
        Generate presentation slides and documentation
        """
        demo_path = Path(demo.demo_files_path)
        
        # Create presentation outline
        presentation_content = f"""
# {demo.title}

## Problem Statement
{opportunity.description}

## Solution Overview
Our automated solution addresses {company.name}'s challenges by:
- Reducing manual processing time by 75%
- Eliminating data entry errors
- Providing real-time insights and reporting

## Technical Implementation
- Technology Stack: {', '.join(demo.technologies_used)}
- Features Demonstrated: {', '.join(demo.features_demonstrated)}
- ROI: {opportunity.roi_percentage:.1f}% annually

## Next Steps
1. Schedule detailed technical review
2. Customize solution for {company.name}
3. Pilot implementation timeline
4. Full deployment and training

## Investment Summary
- Estimated Annual Value: ${opportunity.estimated_value:,.0f}
- Implementation Cost: ${opportunity.implementation_cost:,.0f}
- Payback Period: {opportunity.payback_period_months} months
"""
        
        with open(demo_path / "presentation.md", "w") as f:
            f.write(presentation_content)
        
        # Update demo with presentation URL
        demo.presentation_slides_url = f"{self.staging_url_base}/{demo.id}/presentation.html"
        demo.documentation_url = f"{self.staging_url_base}/{demo.id}/docs"
    
    async def _deploy_demo(self, demo: Demo):
        """
        Deploy demo to staging environment
        """
        demo_id = str(demo.id)
        demo_path = Path(demo.demo_files_path)
        
        # Simulate deployment process
        # In production, this would deploy to actual hosting infrastructure
        
        if demo.demo_type == "web_app":
            # Build React app
            subprocess.run(["npm", "install"], cwd=demo_path, check=True)
            subprocess.run(["npm", "run", "build"], cwd=demo_path, check=True)
            
            demo.demo_url = f"{self.staging_url_base}/{demo_id}"
        
        elif demo.demo_type == "dashboard":
            # Deploy Streamlit app
            demo.demo_url = f"{self.staging_url_base}/streamlit/{demo_id}"
        
        else:
            # For automation scripts, provide download link
            demo.demo_url = f"{self.staging_url_base}/download/{demo_id}"
    
    async def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with context
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception:
            # Return default template if specific template not found
            return self._get_default_template(template_name, context)
    
    def _get_default_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Return default template content when specific template is not available
        """
        if template_name.endswith(".jsx"):
            return f"""
import React from 'react';

function App() {{
  return (
    <div style={{{{padding: '20px', fontFamily: 'Arial, sans-serif'}}}>
      <h1>{context['demo']['title']}</h1>
      <p>Demo for {context['company']['name']}</p>
      <div>
        <h2>Opportunity: {context['opportunity']['title']}</h2>
        <p>{context['opportunity']['description']}</p>
        <p>Estimated Value: ${context['opportunity']['estimated_value']:,.0f}</p>
      </div>
    </div>
  );
}}

export default App;
"""
        elif template_name == "index.html":
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{context['demo']['title']}</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
"""
        else:
            return f"# {context['demo']['title']}\n\nGenerated demo content for {context['company']['name']}"
    
    async def _generate_automation_script(self, company: Company, opportunity: Opportunity, config: Dict[str, Any]) -> str:
        """
        Generate Python automation script
        """
        return f'''"""
Automation Demo for {company.name}
{opportunity.title}

This script demonstrates automated {opportunity.category} capabilities.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import json

class AutomationDemo:
    def __init__(self):
        self.company_name = "{company.name}"
        self.demo_title = "{opportunity.title}"
        
    def run_automation(self):
        """Main automation workflow"""
        print(f"Starting automation demo for {{self.company_name}}")
        
        # Step 1: Data Collection
        data = self.collect_sample_data()
        
        # Step 2: Data Processing
        processed_data = self.process_data(data)
        
        # Step 3: Generate Reports
        report = self.generate_report(processed_data)
        
        # Step 4: Save Results
        self.save_results(report)
        
        print("Automation completed successfully!")
        return report
    
    def collect_sample_data(self):
        """Simulate data collection process"""
        return {{
            "sales": [
                {{"date": "2024-01-01", "amount": 1200, "customer": "Customer A"}},
                {{"date": "2024-01-02", "amount": 850, "customer": "Customer B"}},
                {{"date": "2024-01-03", "amount": 1500, "customer": "Customer C"}}
            ],
            "efficiency_metrics": {{
                "processing_time_before": 120,
                "processing_time_after": 15,
                "time_saved_percentage": 87.5
            }}
        }}
    
    def process_data(self, data):
        """Process and analyze the collected data"""
        df = pd.DataFrame(data["sales"])
        
        return {{
            "total_sales": df["amount"].sum(),
            "average_sale": df["amount"].mean(),
            "customer_count": df["customer"].nunique(),
            "efficiency_improvement": data["efficiency_metrics"]["time_saved_percentage"]
        }}
    
    def generate_report(self, processed_data):
        """Generate automated report"""
        report = f"""
        Automation Report for {{self.company_name}}
        Generated: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
        
        Summary:
        - Total Sales: ${{processed_data['total_sales']:,.2f}}
        - Average Sale: ${{processed_data['average_sale']:,.2f}}
        - Customer Count: {{processed_data['customer_count']}}
        - Efficiency Improvement: {{processed_data['efficiency_improvement']:.1f}}%
        
        Estimated Annual Savings: ${opportunity.estimated_value:,.0f}
        """
        
        return report
    
    def save_results(self, report):
        """Save automation results"""
        with open("automation_report.txt", "w") as f:
            f.write(report)
        
        print("Report saved to automation_report.txt")

if __name__ == "__main__":
    demo = AutomationDemo()
    result = demo.run_automation()
    print(result)
'''
    
    async def _generate_streamlit_dashboard(self, company: Company, opportunity: Opportunity, config: Dict[str, Any]) -> str:
        """
        Generate Streamlit dashboard code
        """
        return f'''import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="{opportunity.title} - Demo",
    page_icon="📊",
    layout="wide"
)

st.title("{opportunity.title}")
st.subheader("Demo Dashboard for {company.name}")

# Sidebar
st.sidebar.markdown("## Dashboard Controls")
date_range = st.sidebar.date_input("Select Date Range", value=[])

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Estimated Annual Savings",
        f"${opportunity.estimated_value:,.0f}",
        delta=f"+{opportunity.roi_percentage:.1f}% ROI"
    )

with col2:
    st.metric(
        "Implementation Cost", 
        f"${opportunity.implementation_cost:,.0f}",
        delta=f"{opportunity.payback_period_months} month payback"
    )

with col3:
    st.metric(
        "Efficiency Improvement",
        "75%",
        delta="+45 hours/week saved"
    )

# Sample charts
st.markdown("## Performance Metrics")

# Create sample data
sample_data = pd.DataFrame({{
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Before Automation': [120, 125, 118, 130, 127, 135],
    'After Automation': [25, 22, 20, 28, 24, 26],
    'Savings': [95, 103, 98, 102, 103, 109]
}})

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        sample_data, 
        x='Month', 
        y=['Before Automation', 'After Automation'],
        title='Processing Time Comparison (Hours)',
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(
        sample_data,
        x='Month',
        y='Savings',
        title='Monthly Time Savings (Hours)',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Additional sections
st.markdown("## Implementation Timeline")
timeline_data = pd.DataFrame({{
    'Phase': ['Analysis', 'Development', 'Testing', 'Deployment', 'Training'],
    'Duration': [2, 4, 2, 1, 1],
    'Status': ['Complete', 'In Progress', 'Planned', 'Planned', 'Planned']
}})

st.dataframe(timeline_data, use_container_width=True)

st.markdown("## Next Steps")
st.write("""
1. **Technical Review**: Schedule a detailed technical review with your team
2. **Customization**: Adapt the solution to {company.name}'s specific needs
3. **Pilot Program**: Start with a small pilot to validate results
4. **Full Deployment**: Roll out across the organization
5. **Training & Support**: Comprehensive training and ongoing support
""")

# Footer
st.markdown("---")
st.markdown("*This demo showcases potential automation capabilities. Actual results may vary based on specific implementation.*")
'''

    def get_demo_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get demo generation metrics for the specified period
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        total_demos = self.db.query(Demo).filter(
            Demo.created_at >= start_date
        ).count()
        
        completed_demos = self.db.query(Demo).filter(
            Demo.created_at >= start_date,
            Demo.status == "ready"
        ).count()
        
        avg_development_time = self.db.query(func.avg(Demo.development_hours)).filter(
            Demo.created_at >= start_date,
            Demo.status == "ready"
        ).scalar() or 0
        
        total_value = self.db.query(func.sum(Opportunity.estimated_value)).join(
            Demo, Demo.opportunity_id == Opportunity.id
        ).filter(
            Demo.created_at >= start_date
        ).scalar() or 0
        
        return {
            "total_demos": total_demos,
            "completed_demos": completed_demos,
            "completion_rate": (completed_demos / total_demos * 100) if total_demos > 0 else 0,
            "average_development_hours": float(avg_development_time),
            "total_opportunity_value": float(total_value),
            "average_value_per_demo": float(total_value / total_demos) if total_demos > 0 else 0
        }


# Demo generation utility functions
async def create_demo_for_opportunity(opportunity_id: int, demo_type: str = "web_app") -> Demo:
    """
    Convenience function to create a demo for an opportunity
    """
    db = next(get_db())
    generator = DemoGenerator(db)
    
    demo_config = {
        "type": demo_type,
        "technologies": ["React", "Python", "JavaScript"],
        "features": ["Automation", "Analytics", "Reporting"],
        "primary_color": "#3B82F6",
        "estimated_hours": 6.0
    }
    
    return await generator.generate_demo(opportunity_id, demo_config)


async def batch_generate_demos(opportunity_ids: List[int]) -> List[Demo]:
    """
    Generate demos for multiple opportunities in batch
    """
    db = next(get_db())
    generator = DemoGenerator(db)
    demos = []
    
    for opportunity_id in opportunity_ids:
        try:
            demo = await generator.generate_demo(opportunity_id, {
                "type": "web_app",
                "technologies": ["React", "Python"],
                "features": ["Automation", "Analytics"]
            })
            demos.append(demo)
        except Exception as e:
            print(f"Failed to generate demo for opportunity {opportunity_id}: {e}")
    
    return demos