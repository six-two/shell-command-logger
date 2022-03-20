from setuptools import setup, find_packages

setup(
    name='shell-command-loggger',
    version='0.1.0',    
    description='Logs the output of commands, so that it can be replayed later',
    url='https://gitlab.com/six-two/shell-command-loggger',
    author='six-two',
    author_email='git@six-two.dev',
    license='MIT License',
    packages=['shell_command_logger'],
    package_dir={"": "src"},
    scripts=['bin/scl', "bin/scl-replay"],
    include_package_data=True,
    install_requires=[
        'termcolor>=1.1.0'                 
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
    ],
)
