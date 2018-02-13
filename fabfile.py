from fabric.api import local, abort, run, roles, cd, env, sudo, lcd, env, settings
from fabric.contrib.console import confirm

env.roledefs = {
    'local': ['localhost'],
    'production': ['root@95.85.60.61']
}

env.roledefs['all'] = [i for j in env.roledefs.values() for i in j]


def commit(message='updating...'):
    """
    commit changes to staging area
    :param message:
    :return:
    """
    local("git add --all")
    with settings(warn_only=True):
        result = local("git commit -m '%s'" % message, capture=True)
        if result.failed and not confirm("Tests failed. Continue anyway?"):
            abort("Aborting at your behest")


def pull():
    """
    update environment
    :return:
    """
    local("git pull")


def push(message='updating...', branch='master', should_commit=True):
    """
    push changes
    :param message
    :return:
    """
    if should_commit is True:
        commit(message)
    local("git push -u origin %s" % branch)


def update_static(python_path='/usr/bin/python', manage_path='manage.py'):
    """
    update static
    :param python_path:
    :param manage_path:
    :return:
    """
    run('%s %s collectstatic' % (python_path, manage_path))


def migrate_database(python_path='/usr/bin/python', manage_path='manage.py'):
    """
    migrate database
    :return:
    """
    run('%s %s makemigrations --merge' % (python_path, manage_path))
    run('%s %s migrate' % (python_path, manage_path))


def ondulate_services(service_paths=list(), cmd='restart'):
    """
    restart list of services
    """
    for _path in service_paths:
        sudo('/usr/sbin/service %s %s' % (_path, cmd))


def deploy():
    """
    update production environment
    :return:
    """
    with cd('/opt/mindcure'):
        sudo('git pull')
        run('. venv/bin/activate')
        ondulate_services(['uwsgi', 'nginx'])


def static_deploy():
    """
    update production environment
    :return:
    """
    with cd('/opt/mindcure'):
        sudo('git pull')
        sudo('. venv/bin/activate')
        update_static(python_path='/opt/mindcure/venv/bin/python')
        ondulate_services(['uwsgi', 'nginx'])


def full_deploy():
    """
    deploy major changes to production, including model changes
    :return:
    """
    with cd('/opt/mindcure'):
        sudo('git pull')
        run('. venv/bin/activate')
        sudo('pip install -r requirements.txt')
        update_static(python_path='/opt/mindcure/venv/bin/python')
        migrate_database(python_path='/opt/mindcure/venv/bin/python')
        ondulate_services(['uwsgi', 'nginx'])


def script(variable="shell"):
    """
    manage.py scripts
    :return:
    """
    local("python manage.py %s" % variable)


def server():
    script('runserver')

