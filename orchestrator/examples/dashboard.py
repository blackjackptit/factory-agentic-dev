#!/usr/bin/env python3
"""
Example: Building a Dashboard
Demonstrates building a more complex analytics dashboard
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from orchestrator import WebsiteOrchestrator


def main():
    """Build an analytics dashboard using the orchestrator"""

    requirements = """
Build an Analytics Dashboard with the following features:

CORE FEATURES:
- Main dashboard layout with sidebar navigation
- Multiple data visualization widgets
- Interactive charts and graphs
- Real-time data updates
- Responsive grid layout

WIDGETS/COMPONENTS:
1. Summary Cards
   - Display key metrics (users, revenue, growth)
   - Icons and colored indicators
   - Percentage change indicators

2. Line Chart
   - Time-series data visualization
   - Multiple data series
   - Interactive tooltips
   - Zoom and pan capabilities

3. Bar Chart
   - Category comparison
   - Horizontal or vertical orientation
   - Hover effects

4. Data Table
   - Sortable columns
   - Pagination
   - Search/filter functionality
   - Export to CSV

5. Pie/Donut Chart
   - Category distribution
   - Interactive legend
   - Percentage labels

LAYOUT:
- Responsive sidebar navigation
- Top header with user profile and notifications
- Grid layout for widgets (drag and drop optional)
- Dark/light theme toggle

DESIGN:
- Modern, professional appearance
- Blue/purple gradient theme
- Smooth animations and transitions
- Loading states for data
- Empty states when no data

TECHNICAL:
- React with TypeScript (preferred)
- State management (Context or Redux)
- Chart library (Recharts or Chart.js)
- Responsive design (mobile-first)
- Mock data for demonstration
    """

    print("Building Analytics Dashboard...")
    print("=" * 70)

    orchestrator = WebsiteOrchestrator(
        project_dir=os.getcwd(),
        output_dir=os.path.join(os.path.dirname(__file__), "../output/dashboard")
    )

    result = orchestrator.build_website(requirements)

    if result.get("success"):
        print("\n✅ Dashboard successfully created!")
        print(f"\nResults: {orchestrator.output_dir}")
    else:
        print("\n❌ Build failed")

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
