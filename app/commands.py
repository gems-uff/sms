import click


def register_commands(app):
    from app.extensions import db
    import app.auth as auth
    import app.main as main

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'main': main, 'auth': auth}

    @app.cli.command()
    def deploy():
        app.logger.info('Deploy started')
        from flask_migrate import upgrade
        app.logger.info('Upgrading database')
        upgrade()
        app.logger.info('Database upgraded')

        app.logger.info('Creating roles and admin user')
        from app.auth.models import User, Role
        Role.insert_roles()
        User.insert_admin()
        app.logger.info('Admin user and roles created successfully')
        from app.main.models import Stock
        Stock.insert_main_stock()
        app.logger.info('main stock created successfully')

    @app.cli.command('t')
    @click.option('--pdb', is_flag=True, help='Enable pdb fallback')
    @click.option('--cov', is_flag=True, help='Enable code coverage')
    @app.cli.command('test')
    @click.option('--pdb', is_flag=True, help='Enable pdb fallback')
    @click.option('--cov', is_flag=True, help='Enable code coverage')
    def test(pdb, cov):
        import pytest
        args = []
        if pdb:
            args += ['--pdb']
        if cov:
            args += [
                '--cov-config', '.coveragerc',
                '--cov=app', 'tests/',
                '--cov-report', 'term',
            ]
        else:
            args += ['--verbose', '-s']
        rv = pytest.main(args)
        exit(rv)
