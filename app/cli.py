import click

from app.extensions import db


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Initialize database tables."""
        with app.app_context():
            db.create_all()
        click.echo("Database initialized.")
