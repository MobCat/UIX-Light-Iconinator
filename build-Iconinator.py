from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ['requests', 'queue', 'sys'], 'excludes': ['email']}

base = 'console'

executables = [
    Executable('Iconinator.py', base=base, icon='icon.ico')
]

setup(name='Iconinator',
      version = '0.3',
      description = 'Automatically build and pack game icons for the games launcher in UIX Light',
      options = {'build_exe': build_options},
      executables = executables)
