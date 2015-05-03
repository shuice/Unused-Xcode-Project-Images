# -*- coding: utf-8 -*-  
# python 2.7,不兼容python 3
# 用来检查图片文件在工程文件中，代码中，目录中的冗余情况
import os
import os.path
import re
import sys

g_regexInSourceCodeFile = r'(?i)@\"([a-z0-9_]*\.(png|jpg))\"'
g_regexInProjectFile = r'(?i) ([a-z0-9_]*\.(png|jpg)) '
g_regexInXibFile = r'(?i)\"([a-z0-9_]*\.(png|jpg))\"'
g_dicName2Source = {} 	# 图片名到源文件的对应关系，找到一个源文件的对应关系即可

# 文件是不是源代码文件，返回True或者False passed
def IsSourceFile(fileName):
	return len(re.findall(r'(?i)\.(mm?|h)$', fileName)) > 0


# 文件是不是xib文件
def IsXibFile(fileName):
	return len(re.findall(r'(?i)\.xib$', fileName)) > 0

# 文件是不是图
def IsImageFile(fileName):
	if '@2x' in fileName:	#2x版本不计算
		return False
	return (len(re.findall(r'(?i)\.(jpg|png)$', fileName)) > 0)


# 获取文件的内容,返回文件行的数组集合 passed
def GetFileContent(filePath):
	fileHandle = open(filePath)
	content = fileHandle.read()
	fileHandle.close()
	return content

def ApplyLowCase(str, wantLowerCase):
	if wantLowerCase:
		return str.lower()
	else:
		return str

# 获取满足函数filter的所有文件
def GetFildetFiles(rootPath, filter, wantFullPath=True, wantLowerCase=False):
	setFiltered = set()	
	for root, dirs, files in os.walk(rootPath):
   		for name in files:
  			if filter(name):
  				if wantFullPath:
  					setFiltered.add(ApplyLowCase(os.path.join(root, name), wantLowerCase))
  				else:
  					setFiltered.add(ApplyLowCase(name, wantLowerCase))
  	return setFiltered	

# 返回在某个源文件中的@"xxx.png"集合
def GetAllPngInSourceFile(filePath):
	fileContent = GetFileContent(filePath)
	matchResult = re.findall(g_regexInSourceCodeFile, fileContent)
	return matchResult

# 返回在某个xib文件中的@"xxx.png"集合
def GetAllPngInXibFile(filePath):
	fileContent = GetFileContent(filePath)
	matchResult = re.findall(g_regexInXibFile, fileContent)
	return matchResult

# 返回在这个目录下所有的源文件中的@"xxx.png"集合
def GetAllPngInAllSourceFile(rootPath):
	if os.path.exists(rootPath) == False:
		print 'directory not found'

	setAllSouceFiles = GetFildetFiles(rootPath, IsSourceFile)

	setallPngNames = set()
	for sourceFile in setAllSouceFiles:
		matchResult = GetAllPngInSourceFile(sourceFile)
		for matchItem in matchResult:
			name = matchItem[0].lower()
			setallPngNames.add(name)
			g_dicName2Source[name] = sourceFile.lower()

	return setallPngNames


# 返回在这个目录下所有的源文件中的@"xxx.png"集合
def GetAllPngInAllXibFile(rootPath):
	if os.path.exists(rootPath) == False:
		print 'directory not found'

	setAllXibFiles = GetFildetFiles(rootPath, IsXibFile)
	setallPngNames = set()
	for sourceFile in setAllXibFiles:
		matchResult = GetAllPngInXibFile(sourceFile)
		for matchItem in matchResult:
			name = matchItem[0].lower()
			setallPngNames.add(matchItem[0].lower())
			g_dicName2Source[name] = sourceFile.lower()

	return setallPngNames

# 返回工程目文件中的png文件
def GetAllPngNamesInProjectFile(rootPath):
	setAllPngNamesInProjectFile = set()
	filePath = rootPath + "/QQMusic.xcodeproj/project.pbxproj"
	fileContent = GetFileContent(filePath)
	matchResult = re.findall(g_regexInProjectFile, fileContent)
	for matchItem in matchResult:
			setAllPngNamesInProjectFile.add(matchItem[0].lower())

	return setAllPngNamesInProjectFile


def PrintSet(setValue, printSource = False):
	for item in setValue:
		if printSource:
			print item, g_dicName2Source[item]
		else:
			print item

# 入口函数
def main():
	#准备好分析的目录	
	rootPath = '/code/4.0'
	imageRootPath = rootPath #+ '/newImages'


	print 'process on directory "', rootPath, '"'
	
	# 三个原始数据，理论上这三个地方的数据应该一样多，但是因为有%d来组装文件名的形势存在，加上宝马项目利用xml定义图片，所以不一致
	# 数据1，从.m,.mm,.h,.h文件中找到的图片名字，没有计算.xml文件，xml文件有两处使用了，一处是宝马，一处是换色，所以这个程序的处理结果需要手工核对
	setAllPngNamesInSource = GetAllPngInAllSourceFile(rootPath).union(GetAllPngInAllXibFile(rootPath))
	# 数据2，从工程文件里面找到的图片名字	
	setAllPngNamesInProjectFile = GetAllPngNamesInProjectFile(rootPath)
	# 数据3，从newImages目录下找到的图片名字	
	setAllImageFileNames = GetFildetFiles(imageRootPath, IsImageFile, False)


	# 分析数据1.存在于工程但是不存在于代码中的图片
	setInProjectNotInSouce = setAllPngNamesInProjectFile.difference(setAllPngNamesInSource)
	# 分析数据2，存在于代码但是不存在于工程图片
	setInSouceNotInProject = setAllPngNamesInSource.difference(setAllPngNamesInProjectFile)
	# 分析数据3，存在于工程但是不存在于目录的图片
	setInProjectNotInDirectory = setAllPngNamesInProjectFile.difference(setAllImageFileNames)
	# 分析数据4，存在于目录但是不存在于工程的图片
	setInDirectoryNotInProject = setAllImageFileNames.difference(setAllPngNamesInProjectFile)
	
	print '原始数据:'
	print len(setAllPngNamesInSource), '个图片存在于代码中'
	print len(setAllPngNamesInProjectFile), '个图片存在于工程中'
	print len(setAllImageFileNames), '个图片存在于目录中'
	
	
	print '\n分析数据，下面的数字越小越好'
	print len(setInProjectNotInSouce), '个图片存在于工程但是不存在于代码中'
	print len(setInSouceNotInProject), '个图片存在于代码但是不存在于工程中'
	print len(setInProjectNotInDirectory), '个图片存在于工程但是不存在于目录中'
	print len(setInDirectoryNotInProject), '个图片存在于目录但是不存在于工程中'

	print '\n---------------------------\n'

	#具体的数据不打印出来了，太长，需要的时候自己打印下
	#PrintSet(setInDirectoryNotInProject, False)

# 主函数调用
main()

