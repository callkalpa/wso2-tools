#!/bin/python

'''
todo:
	pretify output
	read the MANIFEST.MF and get the symbolic name
	comments

'''

import sys
import collections
import xml.etree.ElementTree as ET

def getLicense():
	return """
<!--
~ Copyright (c) 2015, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
~
~ WSO2 Inc. licenses this file to you under the Apache License,
~ Version 2.0 (the "License"); you may not use this file except
~ in compliance with the License.
~ You may obtain a copy of the License at
~
~    http://www.apache.org/licenses/LICENSE-2.0
~
~ Unless required by applicable law or agreed to in writing,
~ software distributed under the License is distributed on an
~ "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
~ KIND, either express or implied.  See the License for the
~ specific language governing permissions and limitations
~ under the License.
-->

"""

def indent(elem, level=0, more_sibs=False):
	i = "\n"
        if level:
		i += (level-1) * '  '
	num_kids = len(elem)
	if num_kids:
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
			if level:
				elem.text += '  '
		count = 0
		for kid in elem:
			indent(kid, level+1, count < num_kids - 1)
			count += 1
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
			if more_sibs:
				elem.tail += '  '
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i
			if more_sibs:
				elem.tail += '  '

def writeXml(root, fileOut):
	f = open(fileOut, 'w')
	f.write('<?xml version="1.0" encoding="utf-8"?>\n')
	f.write(getLicense().strip() + '\n')
	f.write(ET.tostring(root))
	f.close()
	#elementTree.write(fileOut,'UTF-8')

def composeSubElements(parent, subElements):
	for element in subElements:
		tag = ET.SubElement(parent,element)
		tag.text = subElements[element].strip()
	return parent

def processAdvice(advice):
	advice.tag = 'advice'
	values = [x.strip() for x in advice.text.split(':')]
	advice.clear()
	valuesDict = collections.OrderedDict()
	valuesDict['name']=values[0]
	valuesDict['value']=values[1]
	return composeSubElements(advice, valuesDict)

def processBundle(bundle,ver):
	bundle.tag='bundle'
	values = [x.strip() for x in bundle.text.split(':')]
	bundle.clear()
	valuesDict = collections.OrderedDict()
	valuesDict['symbolicName']=values[0]
	valuesDict['version']=values[1]
	return composeSubElements(bundle, valuesDict)

def processImportFeature(feature):
	feature.tag='feature'
	values=[x.strip() for x in feature.text.split(':')]
	feature.clear()
	valuesDict = collections.OrderedDict()
	valuesDict['id']=values[0]
	valuesDict['version']=values[1]
	return composeSubElements(feature, valuesDict)

def processIncludeFeature(feature):
	feature.tag='feature'
	values = [x.strip() for x in feature.text.split(':')]
	feature.clear()
	valuesDict = collections.OrderedDict()
	valuesDict['id']=values[0]
	valuesDict['version']=values[1]
	if len(values) > 2:
		for v in values[2:]:
			temp = v.split('=')
			valuesDict[temp[0]] = temp[1]
	return composeSubElements(feature, valuesDict)
	

def transformXml(root):
	ns = {'ns':'http://maven.apache.org/POM/4.0.0'}

	# change packaging type to carbon-feature
	packaging= root.find('ns:packaging',ns)
	packaging.text='carbon-feature'

	# get carbon-p2-plugin configuration
	cpp = root.find('.//ns:plugin[ns:artifactId="carbon-p2-plugin"]',ns)

	# add extension:true after version tag
	if cpp.find('ns:extensions',ns) is None:
		versionIndex = cpp.getchildren().index(cpp.find('ns:version',ns))
		extensions = ET.Element('extensions')
		extensions.text = 'true'
		cpp.insert(versionIndex+1, extensions)

	execution = cpp.find('ns:executions/ns:execution',ns)

	# change goal to generate
	goal = execution.find('ns:goals/ns:goal',ns)
	goal.text='generate'

	config= execution.find('ns:configuration',ns)

	# remove id
	config.remove(config.find('ns:id',ns))

	# modify property file
	propertyFile=config.find('ns:propertiesFile',ns)
	propertyFile.tag='propertyFile'
	propertyFile.text = 'file:' + propertyFile.text

	# modify advice file
	adviceFile = config.find('ns:adviceFile',ns)
	adviceFile.tag='adviceFileContents'
	advices = adviceFile.findall('.//ns:propertyDef',ns)
	adviceFile.clear()
	for advice in advices:
		adviceFile.append(processAdvice(advice))

	# modify bundles
	bundlesElement = config.find('ns:bundles',ns)
	if bundlesElement is not None:
		bundles = config.findall('.//ns:bundleDef',ns)
		bundlesElement.clear()
		version=root.find('.//ns:parent/ns:version',ns).text
		for bundle in bundles:
			bundlesElement.append(processBundle(bundle, version))	

	# modify import features
	featuresElement = config.find('ns:importFeatures',ns)
	if featuresElement is not None:
		features = config.findall('.//ns:importFeatureDef',ns)
		featuresElement.clear()
		for feature in features:
			featuresElement.append(processImportFeature(feature))

	# modify include features
	featuresElement = config.find('ns:includedFeatures',ns)
	if featuresElement is not None:
		features = config.findall('.//ns:includedFeatureDef',ns)
		featuresElement.clear()
		for feature in features:
			featuresElement.append(processIncludeFeature(feature))

def printUsage():
	print 'Usage: python transform.py <source feature pom path> <target feature pom path>'

def main():
	if not len(sys.argv) > 2:
    		printUsage()
		sys.exit(1)

	fileIn =file(sys.argv[1])
    	fileOut = sys.argv[2]

    	ET.register_namespace('','http://maven.apache.org/POM/4.0.0')
    	elementTree = ET.parse(fileIn)
	root = elementTree.getroot()
    	transformXml(root)
    	writeXml(root,fileOut)

if __name__ == '__main__':
    	main()
