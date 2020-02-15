import re
import subprocess
import Utility
import ParenthesisBalance
import statistics
import copy

class Detect_Sensitive_Code:
    utility = None
    parenthesisBalance = None


    def __init__(self, inputFileName):
        
        self.utility = Utility.Utility()
        self.parenthesisBalance = ParenthesisBalance.Parenthesis_Balance()
        processedFileName = self.removeEmptyLines(inputFileName) #InputB.cpp
        getTrackOfBlock = self.parenthesisBalance.TrackCalculation(processedFileName) #Function, Loop, If track
        processedFileName = self.addBlockwiseLineNumber(processedFileName, getTrackOfBlock) #InputC.cpp
        processedFileName = self.addLineNumberBeforeStatement(processedFileName) #test.cpp
        processedFileName = self.executeProcessedSourceCode(processedFileName)
        self.highlightStatements(processedFileName)
        self.highlightHeuristics(processedFileName , getTrackOfBlock)
        print("Operation Completed")


    def checkIfExists(self, dictData, val):
        for key in dictData.keys():    
            if dictData[key] == val:
                return True
        return False

    def ifInsideBlock(self, dictData, lineNum):
        for st in dictData.keys():    
            ed = dictData[st]
            if st <= lineNum and lineNum <= ed:
                return True
        return False
        
    def addBlockwiseLineNumber(self, inputFileName, trackOfBlock):
        reader = open(inputFileName)
        writer = open("inputC.cpp", "w")
        lines = reader.read().splitlines()
        cnt = 0
        
        if_dict = self.parenthesisBalance.IfTrackCalculation(trackOfBlock)
        else_dict = self.parenthesisBalance.ElseTrackCalculation(trackOfBlock)
        elseIf_dict = self.parenthesisBalance.ElseIfTrackCalculation(trackOfBlock)

        mergedIfElse = dict()
        mergedIfElse.update(if_dict)
        mergedIfElse.update(else_dict)
        mergedIfElse.update(elseIf_dict)


        function_dict = self.parenthesisBalance.FunctionTrackCalculation(trackOfBlock)
        loop_dict = self.parenthesisBalance.LoopTrackCalculation(trackOfBlock)
        loop_level = self.parenthesisBalance.LoopLeveling(loop_dict)

        print("TheKing--> function_dict: ", function_dict)
        print("TheKing--> mergedIfElse_dict: ", mergedIfElse)
        for line in lines:
            cnt = cnt + 1

            strToWrite = ''
            if 'return' in line:
                if self.ifInsideBlock(mergedIfElse, cnt):
                    strToWrite = strToWrite + 'printf("ifelse_end_id %d\\n", global_ifelse_id--);'
                if self.ifInsideBlock(loop_dict, cnt):
                    strToWrite = strToWrite + 'printf("loop_end_id %d\\n", global_loop_id--);'
                if self.ifInsideBlock(function_dict, cnt):
                    strToWrite = strToWrite + 'printf("function_end_id %d\\n", global_function_id--);'
                strToWrite = strToWrite + line 
                
                writer.write(strToWrite)
                writer.write('\n')
                continue
            
            if (cnt - 1) in function_dict:
                line += 'printf("function_start_id %d\\n", ++global_function_id);'
            if self.checkIfExists(function_dict, cnt):
                line = 'printf("function_end_id %d\\n", global_function_id--);' + line
            if (cnt - 1) in mergedIfElse:
                line += 'printf("ifelse_start_id %d\\n", ++global_ifelse_id);'
            if self.checkIfExists(mergedIfElse, cnt):
                line = 'printf("ifelse_end_id %d\\n", global_ifelse_id--);' + line
            if (cnt) in loop_dict:
                line = 'printf("loop_start_id %d\\n", ++global_loop_id);' + line
            if self.checkIfExists(loop_dict, cnt):
                line += 'printf("loop_end_id %d\\n", global_loop_id--);'          

            writer.write(line)
            writer.write('\n')
        
        writer.close()
        reader.close()

        return "inputC.cpp"



    def removeEmptyLines(self, inputFileName):
        f = open (inputFileName)
        lines = f.read().splitlines()
        f.close()

        fileName = "inputB.cpp"
        f = open(fileName, "w")
        line = "static int global_loop_id = 0, global_ifelse_id = 0, global_function_id = 0;"
        f.write(line)
        f.write("\n")
        


        write_statement = ""
        done = 0 
        for line in lines:
            if(line==""):
                continue
            #ADDING NEW_STATEMENT (freopen OUT)#
            if("int main()" in write_statement and ("{" in write_statement) and done == 0):
                f.write(line)
                f.write('\n')
                f.write('freopen("outputC.txt", "w+", stdout);')
                f.write('\n')
                done = 1
            else:
                res = self.utility.Statement_Get(line)
                if self.utility.Loop_Check(line) == False:
                    if len(res) > 0:
                        for x in res:
                            f.write(x)
                            f.write('\n')
                    else:
                        f.write(line)
                        f.write('\n')
                else:
                    f.write(line)
                    f.write('\n')

            if( (line == "int main()" or line == "{") and done == 0 ):
                write_statement += line
        f.close()
        return fileName


    def addLineNumberBeforeStatement(self, inputFileName):
        print("TheKing--> ", inputFileName)

        f = open (inputFileName)
        lines = f.read().splitlines()
        f.close()
        fileName = "test.cpp"
        f = open(fileName, "w")
        cnt = 0
        for line in lines:
            if "global_loop_id" in line or "global_ifelse_id" in line or "global_function_id" in line:
                f.write(line)
                f.write('\n')
                continue
            cnt+=1
            if cnt == 1:
                continue

            if(line==""):
                continue

            words = line.split()
                
            #FUNCTION CHECK#
            if self.utility.Function_Check(line) == True:
                f.write(line)
                f.write('\n')
                continue

            #STATEMENT CHECK#
            if "using" in words and "namespace" in words:
                f.write(line)
                f.write('\n')
                continue

            res = self.utility.Statement_Get(line)
            if self.utility.Loop_Check(line) == False:
                if len(res) > 0:
                    for x in res:
                        f.write('printf("line = %d\\n",__LINE__);')
                        f.write(x)
                        f.write('\n')
                else:
                    f.write(line)
                    f.write('\n')
            else:
                f.write(line)
                f.write('\n')
        f.close()
        return fileName


    def executeProcessedSourceCode(self, inputFileName):
        cmd = inputFileName
        subprocess.call(["g++","-o", "b", cmd]) 
        subprocess.call("b.exe")
        return "outputC.txt"


    def getColorByRank(self, rank):
        if rank == 4:
            return "red"
        if rank == 3:
            return "orange"
        if rank == 2:
            return "blue"
        if rank == 1:
            return "#00d600"
        return "black"
        

    def highlightStatements(self, inputFileName):

        f2 = open('outputC.txt')
        l2 = f2.read().splitlines()

        lineNumbers = []
        for line in l2:
            word = line.split()
            if word[0]=='line':
                lineNumbers.append(int(word[2]))

        rank = dict()
        countTrac = dict()
        tempList = copy.deepcopy(lineNumbers)

        for x in tempList:
            if x not in countTrac.keys():
                countTrac[x] = 1
            else:
                countTrac[x] += 1
        
        #print(countTrac)

        sorted_x = sorted(countTrac.items(), key=lambda kv: kv[1])
        sorted_x.reverse()
        #print(sorted_x)
        max_freq = sorted_x[0][1]
        min_freq = sorted_x[len(sorted_x)-1][1]




        resRank = 0
        for (lineNumber, freq) in sorted_x:
            if freq >= max_freq:
                resRank = 4
            elif freq == min_freq :
                resRank = 1
            elif freq == 2:
                resRank = 2
            elif freq<max_freq and freq>2:
                resRank = 3
            else:
                resRank = 0
            rank[lineNumber] = self.getColorByRank(resRank)
                
            

        #print(lineNumbers)

        f3 = open('inputB.cpp')
        l3 = f3.read().splitlines()

        counter = 0
        stringfff = "<html><body><code>\n"
        for line in l3:

            if(line.startswith("#")):
                line = self.utility.Handeling_HeaderFile(line)

            counter = counter + 1
            if(line == 'freopen("outputC.txt", "w+", stdout);'):
                stringfff += ''
                
            elif counter in lineNumbers:
                cc = 0
                for x in lineNumbers:
                    if x == counter:
                        cc+=1
            
                if counter in rank.keys():
                    curColor = rank[counter]
                else:
                    curColor = "black"
                
                if curColor =="red":    
                    stringfff += '<p style="font-family:verdana;font-weight:bold;color:'+curColor+'">' + line + '   //(MOST SENSITIVE portion), executed ' + str(cc) + ' times' + '</p>\n'
                elif cc == 1:
                    stringfff += '<p style="font-family:verdana;font-weight:bold;color:'+curColor+'">' + line + '</p>\n'
                else:
                    stringfff += '<p style="font-family:verdana;font-weight:bold;color:'+curColor+'">' + line + '   //executed ' + str(cc) + ' times' + '</p>\n'    

            else:
                stringfff += '<p style="font-family:verdana;font-weight:bold;color:black">' + line + '</p>\n'
            

        stringfff += "</code></body></html>\n"

        f2.close()
        f3.close()
        f = open("report.html", "w")
        f.write(stringfff)
        f.close()


    def calculateOccurrences(self, linenumbers, st, ed):
        cnt = 0
        for i in range(0, len(linenumbers)):
            if st <= linenumbers[i] and linenumbers[i] <= ed:
                cnt+=1
        return cnt

    def highlightHeuristics(self, inputFileName , trackOfBlock):
        f2 = open(inputFileName)
        l2 = f2.read().splitlines()
        f2.close()
        lineNumbers = []
        for line in l2:
            word = line.split()
            if word[0]=='line':
                lineNumbers.append(int(word[2]))
        
        for x in sorted(lineNumbers):
            print(x)
        
        '''
        print("-- ---- ")
        for i in trackOfBlock.keys():
            print(str(i) + ' ' + str(trackOfBlock[i]))
        '''

        if_dict = self.parenthesisBalance.IfTrackCalculation(trackOfBlock)
        else_dict = self.parenthesisBalance.ElseTrackCalculation(trackOfBlock)
        elseIf_dict = self.parenthesisBalance.ElseIfTrackCalculation(trackOfBlock)
        function_dict = self.parenthesisBalance.FunctionTrackCalculation(trackOfBlock)
        loop_dict = self.parenthesisBalance.LoopTrackCalculation(trackOfBlock)
        loop_level = self.parenthesisBalance.LoopLeveling(loop_dict)
        
        
        for i in sorted(loop_level):
            print(str(i) + '-> ' + str(loop_level[i]))

        for i in sorted(loop_level):
            (ed,level) = loop_level[i]
            print(str(i)+ '-> ' + str(ed) + ': ' + str(self.calculateOccurrences(lineNumbers, i, ed)))
        
        

def main():
    obj = Detect_Sensitive_Code("EDCproneCode.cpp")

if __name__ == '__main__':
    main()