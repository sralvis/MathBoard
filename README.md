# MathBoard

**Advanced Engineering Whiteboard for Math Calculations**

MathBoard is a document-centric workspace inspired by Mathcad, designed to merge the documentation of engineering intent with the execution of complex calculations.

## ✨ Key Features

-   **Whiteboard Workspace**: A What-You-See-Is-What-You-Get (WYSIWYG) interface allowing arbitrary placement of math and text regions.
-   **Intelligent Math Engine**: Powered by SymPy for numeric and symbolic calculations.
-   **Reading Order Evaluation**: Regions are evaluated based on their position (top-to-bottom, left-to-right), respecting variable scoping.
-   **Global & Local Definitions**: Supports local assignments (`:=`) and worksheet-wide global definitions (`≡`).
-   **Symbolic Evaluation**: Use the `->` operator for algebraic simplification and manipulation.
-   **Integrated Plotting**: Create dynamic charts directly in the workspace using the `plot(f(x), x, start, end)` command.
-   **Grid Snapping**: Precise alignment of regions with an interactive background grid.
-   **Modern Ribbon UI**: Categorized engineering workflow tools (Math, Data, Plots, Calculation).

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   Modern Web Browser (Chrome/Edge/Firefox)

### Running the Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Start the Flask server:
    ```bash
    python app.py
    ```
    The engine will be available at `http://localhost:5000`.

### Running the Frontend

1.  Open `frontend/index.html` directly in your web browser.
2.  Alternatively, use a local development server:
    ```bash
    npx serve frontend
    ```

## 🛠 Usage Tips

-   **Double-Click**: Create a new Math Region.
-   **Right-Click**: Create a new Text Region.
-   **Drag & Drop**: Move regions to reorganize your worksheet. The calculation results will update automatically based on the new positions.
-   **Global Definitions**: Use the `\equiv` button (or type `\equiv` in LaTeX) to define variables that are accessible everywhere.
-   **Plotting**: Try typing `plot(\sin(x), x, 0, 10)` to see a live graph.