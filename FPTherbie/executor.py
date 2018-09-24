import os
import sys
import shutil

def extractBounds(filename):
	origExpress=[]
	origBounds=[]
	origResults=open(filename).read()
	origExpress=origResults.split("Problem:")
	origExpress=origExpress[1:]
	for val in origExpress:
		elem=val.split("\n")
		for absVal in elem:
			if "Absolute error (exact)" in absVal:
				values=absVal.split(":")
				origBound=float(values[1])
				origBounds.append(origBound)
	return origBounds

def checkBounds(orig,new):
	retVal=True
	for i in range(0,len(orig)):
		if orig[i]<new[i]:
			retVal=False
			break
	return retVal

herbieFolder="<path>/herbie/";
FPTaylorFolder="<path>/FPTaylor/";
fpbBenchTools="<path>/FPBench/";
inputFolder="<path>/Benchmarks/"

if os.path.exists("./tmp"):
	shutil.rmtree("./tmp")
os.makedirs("./tmp")

for filename in os.listdir(inputFolder):
	if ".txt" in filename:
		forcedMode=False
		if "-force" in sys.argv[1:]:
			forcedMode=True
		fileName=str(filename[0:-4])
		os.makedirs("./tmp/"+fileName)
		origFile=open(inputFolder+filename).read()
		cleanOrigFile=origFile.replace("\n","").replace(";","")
		expressions=cleanOrigFile.split("Expressions")
		listExpressions=expressions[1].split(",")
		listExpressions = [elem.strip() for elem in listExpressions]
		for index,expr in enumerate(listExpressions):
			newFile="".join(origFile)
			for elem in listExpressions:
				if not elem==expr:
					newFile=newFile.replace(elem+",","").replace(elem,"")
				else:
					newFile=newFile.replace(elem+",",elem)
			newFileName="./tmp/"+fileName+"/"+fileName+"_Expr_"+str(index)
			newFilename=newFileName+".txt"
			f=open(newFilename,"w+")
			f.write(newFile)
			f.close()
			resultFilename=newFileName+"_RES.txt"
		
		#filename and fileName ok
		#newfilename newFileName and resultFileName cambiano
		for i in range(0,len(listExpressions)):
			newFileName="./tmp/"+fileName+"/"+fileName+"_Expr_"+str(i)
			newFilename=newFileName+".txt"
			resultFilename=newFileName+"_RES.txt"			
			exe0=FPTaylorFolder+ "fptaylor "+newFilename +"> "+resultFilename
			print "\n###############################"
			print "###############################\n"
			print newFileName
			val0=os.system(exe0)
			if val0==0:
				print "FPTaylor on original expression succeed."
			else:
				print "FPTaylor FAILURE on original expression"	
			
			origBounds=extractBounds(resultFilename)
			print "Error bound of the original expression:"+str(origBounds)
			exe=FPTaylorFolder+ "fptaylor --fpcore-out "+newFileName+".fpcore "+newFilename
			val=os.system(exe);
			if (val==0):
				points=256
				iterats=1
				n=0
				newFileNameOPT=newFileName+"_OPT.fpcore"
				while True:
					forbExpress=0
					while True:
						exe2="racket "+herbieFolder+"src/herbie.rkt improve --num-points "+str(points)+" --num-iters "+str(iterats)+" "+newFileName+".fpcore "+newFileNameOPT
						val2=os.system(exe2);
						if val2==0:
							tmp=open(newFileNameOPT).read()
							if (not 'pow' in tmp) and (not 'cbrt' in tmp):
								print "Herbie rewrites succesfull!"
								break
							else:
								print "POW or cbrt in file!"
								forbExpress=forbExpress+1
					#--auto-file-names 
					exe3="racket "+fpbBenchTools+"tools/core2fptaylor.rkt --auto-file-names --files --out-path ./tmp/"+fileName+" < "+newFileNameOPT
					val3=os.system(exe3)
					if val3==0:
						try:
							newBounds=[]
							exprName=((expr.split("=")[0]).strip().split())[0]
							fileHerbie="./tmp/"+fileName+"/"+exprName+".txt" 
							os.rename("./tmp/"+fileName+"/"+"ex0.txt", fileHerbie)
							print fileHerbie
							exe4=FPTaylorFolder+ "fptaylor "+fileHerbie +">"+newFileName+"_"+str(index)+"_OPT_RES.txt"
							val4=os.system(exe4);
							if val4==0:
								print "succed fptaylor on optimization: expression_"+str(index)
							else:
								print "failure fptaylor on optimization: expression_"+str(index)
			
							newBounds.append(extractBounds(newFileName+"_"+str(index)+"_OPT_RES.txt")[0])	
							print "Error bound of the new expression:"+str(newBounds)
							boundSat=checkBounds(origBounds,newBounds)
							if not forcedMode:
								break
							if forcedMode and boundSat: #forceMode equals true
								break
							if forbExpress>=8:
								n=3
							points=points*2
							iterats=iterats+1
							
							if iterats==4:
								points=256
								iterats=1
								n=n+1
							print "Force Mode enabled: iterate again! Points:"+str(points)+", Iters:"+str(iterats)
						
						except Exception, e:
							print "FAILURE: "+ str(e)
							n=n+1
						
						finally:
							if n==3:
								print "REWRITE FAILS NO IMPROVEMENT!"
								break
					else: 
						print "\n\nHerbie to FPTaylor fails\n\n"
						break
			else:
				print "\n\nHerbie Optimizer fails!\n\n"
	
