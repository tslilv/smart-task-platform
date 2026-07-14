"""Entry point for Smart Task Platform."""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)