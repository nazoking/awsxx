from distutils.core import setup
setup(name='awsxx',
      description='AWS High-level utilities',
      url='https://github.com/nazoking/awsxx',
      version='0.0.5',
      author='nazoking',
      author_email='nazoking@gmail.com',
      requires=[
          'PyYAML',
          'boto',
          'Fabric'
          ],
      packages=[
          'awsxx',
          'awsxx.lib',
          'awsxx.copy'
          ],
      scripts=[
          'scripts/ec2-copy'
          ]
      )
