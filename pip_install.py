import pip
from subprocess import call

requirements = []

r = open('requirements.txt', 'r')
for line in r:
    requirements.append(line)
r.close()

for package in requirements:
    call("pip install " + package, shell=True)
