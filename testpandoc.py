try:
   import pypandoc
   description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   description = ''
print(description)