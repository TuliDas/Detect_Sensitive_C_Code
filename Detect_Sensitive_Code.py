import re
import subprocess
import statistics
import copy
import Utility
import ParenthesisBalance
import HighlightExecutedStatements
import HighlightHeuristics
import allPossibleFaultInjectionBit
import RatioWithRespectToExecutionTime

class Detect_Sensitive_Code:
    
    utility = None
    parenthesisBalance = None
    highlightStatements = None
    highlightHeuristics = None
    faultyBinaryBit = None  
    ratioExecutionTime = None 

    def __init__(self, inputFileName):
        
        self.utility = Utility.Utility()
        self.parenthesisBalance = ParenthesisBalance.Parenthesis_Balance()
        self.highlightStatements = HighlightExecutedStatements.Highlight_Executed_Statements()
        self.highlightHeuristics = HighlightHeuristics.Highlight_Heuristics()
        self.faultyBinaryBit = allPossibleFaultInjectionBit.Faulty_Binary_Bit()
        self.ratioExecutionTime = RatioWithRespectToExecutionTime.Ratio_Execution_Time()
        
        
        processedFileName = self.removeEmptyLines(inputFileName) # -> InputA.cpp
        allFunctionName = self.getAllFunctionName(processedFileName) #-> allFunctionName
        getTrackOfBlock,start_main = self.parenthesisBalance.TrackCalculation(processedFileName) #Function, Loop, If track
        justBlock = self.updateBlock(getTrackOfBlock)  # -> block start and end report
        inputString = self.inputToString(processedFileName)
        #print(getTrackOfBlock)
        e1,e2,e3,total_time = self.addExecutionClockFuntionBlockWise(processedFileName, getTrackOfBlock,justBlock,inputString,allFunctionName) #InputE.cpp
        self.ratioExecutionTime.blockWiseExecutionTimePercentage(total_time,e1,e2,e3,inputString)
        processedFileName = self.addLineNumberBeforeStatement(processedFileName,justBlock,start_main) # -> InputB.cpp
        processedFileName = self.addBlockwiseLineNumber(processedFileName, getTrackOfBlock,justBlock) #-> inputC.cpp
        processedFileName = self.executeProcessedSourceCode(processedFileName)
        self.highlightStatements.highlightExecutedStatements(processedFileName)
        b1,b2,b3 = self.getAllHeuristicsAndHighlight(processedFileName , getTrackOfBlock, allFunctionName, inputString)
        fullBinaryBit = self.faultyBinaryBit.wholePossibleBinaryBit(processedFileName)
        self.faultyBinaryBit.blockWisePossibleBit(fullBinaryBit,b1,b2,b3,inputString)
        print("Operation Successful")
        

    def removeEmptyLines(self, inputFileName):
        f = open (inputFileName)
        lines = f.read().splitlines()
        f.close()

        fileName = "InputA.cpp"
        f = open(fileName, "w")

        line = "static int global_loop_id = 0, global_ifelse_id = 0, global_function_id = 0;"
        f.write(line)
        f.write("\n")
        
        line = "#include <chrono>"
        f.write(line)
        f.write("\n")
        line = "long long getTicks(){return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();}"
        f.write(line)
        f.write("\n")
        
        done = 0 
        for line in lines:

            if line == "":
                f.write(line)
                continue

            if(line.startswith("int main()") and done == 0):
                done += 1
                f.write(line)
                f.write('\n')
                continue

            elif(done == 1):
                done+=1
                ffi = 'freopen("Input.txt", "r+", stdin);'
                ffo = 'freopen("Output.txt", "w+", stdout);'
                f.write(line + ' ' + ffi + ' '+ ffo)
                f.write('\n')

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

        f.close()
        return fileName

    def inputToString(self,inputFileName):
        f = open (inputFileName)
        lines = f.read().splitlines()
        f.close()
        strr = []
        strr.append('begin')

        for line in lines:
            line = line.strip()
            strr.append(line)
        return strr

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
    
    def getStartingLineNumber(self, dictData, lineNum):
        for st in dictData.keys():
            if dictData[st] == lineNum:
                return st
        return None

    def getBlockRange(self, funcData, lineNum):
        for st in funcData.keys():    
            ed = funcData[st]
            if st <= lineNum and lineNum <= ed:
                return (st,ed)
        return None

    def executeTimeOptimalHeuristicts(self,dict_data):
        H = []
        h = []
        mx = -1
        for i in dict_data.keys():
            if dict_data[i] > mx:
                mx = dict_data[i]
        
        for i in dict_data.keys():
            if dict_data[i] == mx:
                (a,b) = i 
                H.append(a)
                for j in range(a,b+1):
                    h.append(j)

        #print(H)
        #print(h)
        return H,h


    def addExecutionClockFuntionBlockWise(self, inputFileName, trackOfBlock,blockTrack,strr,fn_name):
        reader = open(inputFileName)
        fileName = "InputE.cpp"
        writer = open(fileName, "w")
        lines = reader.read().splitlines()
        
        if_dict = self.parenthesisBalance.IfTrackCalculation(trackOfBlock)
        else_dict = self.parenthesisBalance.ElseTrackCalculation(trackOfBlock)
        elseIf_dict = self.parenthesisBalance.ElseIfTrackCalculation(trackOfBlock)
        mergedIfElse = dict()
        mergedIfElse.update(if_dict)
        mergedIfElse.update(else_dict)
        mergedIfElse.update(elseIf_dict)
        function_dict = self.parenthesisBalance.FunctionTrackCalculation(trackOfBlock)
        loop_dict = self.parenthesisBalance.LoopTrackCalculation(trackOfBlock)

        cnt = 0
        trackerCnt = 0
        for line in lines:
            cnt = cnt + 1
            
            if 'return' in line and self.ifInsideBlock(blockTrack,cnt):
                if self.ifInsideBlock(function_dict, cnt):
                    (startingPoint, endPoint) = self.getBlockRange(function_dict, cnt)
                    line = 'printf("Time = %lld , ( ' +str(startingPoint)+' , '+str(endPoint)+' ) \\n", getTicks() - startTime'+str(startingPoint)+');' + line
                
                writer.write(line)
                writer.write('\n')
                continue

            
            if (cnt - 1) in function_dict:
                line += 'auto startTime' + str(cnt-1)+' = getTicks();'
                trackerCnt+=1
            if self.checkIfExists(function_dict, cnt):
                startingPoint = self.getStartingLineNumber(function_dict, cnt)
                line = 'printf("Time = %lld , ( ' +str(startingPoint)+' , '+str(cnt)+' ) \\n", getTicks() - startTime'+str(startingPoint)+');' + line
                trackerCnt-=1
            if (cnt - 1) in mergedIfElse:
                line += 'auto startTime' + str(cnt-1)+' = getTicks();'
                trackerCnt+=1
            if self.checkIfExists(mergedIfElse, cnt):
                startingPoint = self.getStartingLineNumber(mergedIfElse, cnt)
                line = 'printf("Time = %lld , ( ' +str(startingPoint)+' , '+str(cnt)+' ) \\n", getTicks() - startTime'+str(startingPoint)+');' + line
                trackerCnt-=1
            if (cnt) in loop_dict:
                line = 'auto startTime' + str(cnt)+' = getTicks();' + line
                trackerCnt+=1
            if self.checkIfExists(loop_dict, cnt):
                startingPoint = self.getStartingLineNumber(loop_dict, cnt)
                line += 'printf("Time = %lld , ( ' +str(startingPoint)+' , '+str(cnt)+' ) \\n", getTicks() - startTime'+str(startingPoint)+');'
                trackerCnt-=1          

            writer.write(line)
            writer.write('\n')
        
        writer.close()
        reader.close()

        cmd = fileName
        subprocess.call(["g++", "-std=c++11", "-o", "e", cmd]) 
        subprocess.call("e.exe")

        fileName = "Output.txt"
        reader = open(fileName, "r")
        lines = reader.read().splitlines()
        ifelse_exe = {}
        loop_exe = {}
        function_exe = {}

        for line in lines:
            if "Time" in line:
                words = line.split()
                startBlock = int(words[5])
                endBlock = int(words[7])
                time = int(words[2])
                

                if startBlock in function_dict.keys() and function_dict[startBlock]==endBlock:
                    if (startBlock, endBlock) in function_exe:
                        function_exe[(startBlock, endBlock)] += time
                    else:
                        function_exe[(startBlock, endBlock)] = time
                elif startBlock in mergedIfElse.keys() and mergedIfElse[startBlock]==endBlock:
                    if (startBlock, endBlock) in ifelse_exe:
                        ifelse_exe[(startBlock, endBlock)] += time
                    else:
                        ifelse_exe[(startBlock, endBlock)] = time
                elif startBlock in loop_dict.keys() and loop_dict[startBlock]==endBlock:
                    if (startBlock, endBlock) in loop_exe:
                        loop_exe[(startBlock, endBlock)] += time
                    else:
                        loop_exe[(startBlock, endBlock)] = time

    
        total_execution_time = 0
        for i in function_exe.keys():
            a = i[0]
            if 'main()' in strr[a]:
                total_execution_time = function_exe[i]
                del function_exe[i]
                break
        


        H1,h1 = self.executeTimeOptimalHeuristicts(ifelse_exe)
        H2,h2 = self.executeTimeOptimalHeuristicts(loop_exe)
        H3,h3 = self.executeTimeOptimalHeuristicts(function_exe)

        fn_name = self.updateFunctionName(function_dict,fn_name,strr)
        #print(fn_name)

        temp = []
        #print(fn)
        for i in H3:
            for j in fn_name.keys():
                if j == self.utility.Function_DeclarationName(strr[i]):
                    for x in fn_name[j]:
                        temp.append(x)
        for i in temp:
            H3.append(i)
        
        self.highlightHeuristics.highlightingHeuristics(inputFileName,H1,h1,H2,h2,H3,h3,"executeTime.html")
        return ifelse_exe,loop_exe,function_exe,total_execution_time


    def addLineNumberBeforeStatement(self, inputFileName,blockTrack,start_main):
        f = open (inputFileName)
        lines = f.read().splitlines()
        f.close()
        fileName = "InputB.cpp"
        f = open(fileName, "w")

        write_statement = 'freopen("Output.txt", "w+", stdout);'
        cnt = 0

        for line in lines:
            cnt+=1
            
            

            if "global_loop_id" in line and "global_ifelse_id" in line and "global_function_id" in line:
                f.write(line)
                f.write('\n')
                continue
            if (write_statement in line):
                f.write(line)
                f.write('\n')
                continue

            #if ( self.ifInsideBlock(blockTrack , cnt) == False):
                #f.write(line)
                #f.write('\n')
                #continue


            if (  ("{" in line) or ("}" in line) ):
                f.write(line)
                f.write('\n')
                continue

            if(line==""):
                continue

            words = line.split()
                
            #FUNCTION CHECK , LOOP CHECK#
            if self.utility.Function_Check(line) == True or self.utility.Loop_Check(line) == True:
                f.write(line)
                f.write('\n')
                continue

            #HEADER CHECK#
            if "using" in words and "namespace" in words:
                f.write(line)
                f.write('\n')
                continue
            #  or
            #print(str(cnt) + ' -> ' + line)
            if  self.utility.Statement_Check(line) and  (self.ifInsideBlock(blockTrack,cnt) or (cnt >= start_main) ) :
                    f.write('printf("line = %d\\n",__LINE__);')
                    f.write(line)
                    f.write('\n')
            else:
                f.write(line)
                f.write('\n')

        f.close()
        return fileName


    def updateBlock(self,info):
        #print(info)
        temp = {}
        for i in info.keys():
            temp[i] = info[i][0]

        #print(temp)
        return temp

    def addBlockwiseLineNumber(self, inputFileName, trackOfBlock,blockTrack):
        reader = open(inputFileName)
        fileName = "InputC.cpp"
        writer = open(fileName, "w")
        lines = reader.read().splitlines()
        
        if_dict = self.parenthesisBalance.IfTrackCalculation(trackOfBlock)
        else_dict = self.parenthesisBalance.ElseTrackCalculation(trackOfBlock)
        elseIf_dict = self.parenthesisBalance.ElseIfTrackCalculation(trackOfBlock)

        mergedIfElse = dict()
        mergedIfElse.update(if_dict)
        mergedIfElse.update(else_dict)
        mergedIfElse.update(elseIf_dict)


        function_dict = self.parenthesisBalance.FunctionTrackCalculation(trackOfBlock)
        loop_dict = self.parenthesisBalance.LoopTrackCalculation(trackOfBlock)
        #loop_level = self.parenthesisBalance.LoopLeveling(loop_dict)

        cnt = 0
        for line in lines:
            cnt = cnt + 1

            strToWrite = ''
            if 'return' in line and self.ifInsideBlock(blockTrack,cnt):
                ss = self.utility.Statement_Get(line)
                if self.ifInsideBlock(mergedIfElse, cnt):
                    strToWrite = strToWrite + 'printf("ifelse_end_id %d line = %d\\n", global_ifelse_id--, __LINE__);'
                if self.ifInsideBlock(loop_dict, cnt):
                    strToWrite = strToWrite + 'printf("loop_end_id %d line = %d\\n", global_loop_id--, __LINE__);'
                if self.ifInsideBlock(function_dict, cnt):
                    strToWrite = strToWrite + 'printf("function_end_id %d line = %d\\n", global_function_id--, __LINE__);'
                strToWrite = ss[0] + strToWrite + ss[1] 
                
                writer.write(strToWrite)
                writer.write('\n')
                continue
            
            if (cnt - 1) in function_dict:
                line += 'printf("function_start_id %d line = %d\\n", ++global_function_id, __LINE__);'
            if self.checkIfExists(function_dict, cnt):
                line = 'printf("function_end_id %d line = %d\\n", global_function_id--, __LINE__);' + line
            if (cnt - 1) in mergedIfElse:
                line += 'printf("ifelse_start_id %d line = %d\\n", ++global_ifelse_id, __LINE__);'
            if self.checkIfExists(mergedIfElse, cnt):
                line = 'printf("ifelse_end_id %d line = %d\\n", global_ifelse_id--, __LINE__);' + line
            if (cnt) in loop_dict:
                line = 'printf("loop_start_id %d line = %d\\n", ++global_loop_id, __LINE__);' + line
            if self.checkIfExists(loop_dict, cnt):
                line += 'printf("loop_end_id %d line = %d\\n", global_loop_id--, __LINE__);'          

            writer.write(line)
            writer.write('\n')
        
        writer.close()
        reader.close()
        return fileName

    def executeProcessedSourceCode(self, inputFileName):
        cmd = inputFileName
        outputFileName = "Output.txt"

        subprocess.call(["g++","-std=c++11", "-o", "b", cmd]) 
        subprocess.call("b.exe")
        return outputFileName 

    def calculateStatementsForHeuristics(self, instruction_set):
        instruction_set.append([-1, -1])
        ret = {}
        st = []
        st.append([-1,-1])
        for ls in instruction_set:
            sz = len(st)
            if ls[0] == 0:
                for ss in st:
                    tup = (ss[0], ss[1])
                    if tup in ret:
                        ret[tup] += 1
                    else:
                        ret[tup] = 1
            elif ls[0] == st[sz - 1][0]:
                st.pop()
            else:
                st.append(ls)
        
        return ret

    def calculateFunctioncallLevel(self, fn_list, loop_list):
        ret = {}
        st = []
        st.append([-1,-1])
        for ls in loop_list:
            sz = len(st)
            if ls[0] == 0:
                for ln in fn_list:
                    if ln[0] == ls[1]:
                        ret[ln] = sz
                        break
            elif ls[0] == st[sz - 1][0]:
                st.pop()
            else:
                st.append(ls)
        ret_dic = {}
        for rr in ret.keys():
            ret_dic[rr[1]] = []
        for rr in ret.keys():
            lineno = rr[0]
            fn_name = rr[1]
            cnt = ret[rr]
            ret_dic[fn_name].append((lineno, cnt))
        for fn in ret_dic:
            mini = 99999
            for val in ret_dic[fn]:
                mini = min(mini, val[1])
            new_list = []
            for val in ret_dic[fn]:
                if val[1] == mini:
                    new_list.append(val)
            ret_dic[fn] = new_list
        #print(ret_dic)
        return ret


    def getAllFunctionName(self, inputFileName):
        f = open (inputFileName)
        lines = f.read().splitlines()
        cnt = 0
        ret = []
        for line in lines:
            cnt += 1
            line = line.strip()
            res = self.utility.Function_CallName(line)
            if(res == 'null'):
                continue
            else:
                ret.append((cnt, res))
        return ret
    
    def getOptimalHeuristics(self,info):
        #print(info)
        ans = []
        mx_freq = -1
        for i in info.keys():
            if(i[0] == 1):
                if info[i] >= mx_freq:
                    mx_freq = info[i]

        for i in info.keys():
            if info[i] == mx_freq and i[0] == 1:
                ans.append(i[1])

        #print(ans)
        return ans

    def getFunctionStatement(self,info):
        ans = {}

        for i in info.keys():
            if(i[0] == -1):
                continue
            ans[i[1] - 1] = info[i]

        ans = sorted(ans.items(), key=lambda kv: kv[1])
        return ans  
    
    def findFunctionDefinition(self, inputFileName ,info,H3,fun):
        fun2 = {}
        f2 = open(inputFileName)
        l2 = f2.read().splitlines()
        f2.close()

        for i in info:
            strr = i
            cnt = 0

            for line in l2:
                cnt += 1
                
                if( cnt not in fun.keys()):
                    continue
                
                if (strr in line) and (cnt in fun.keys()):
                    fun2[cnt] = fun[cnt]  
        
        cnt = 0
        for line in l2:
            cnt += 1
            if ( ( 'return' in line ) and self.ifInsideBlock(fun2,cnt) ) :
                H3.append(cnt)

        #print(H3)    
        return H3

    def discardBuiltInFunction(self,level,track):
        l1 = []
        l2 = []
        for i in track.keys():
            l1.append(i)
        
        for i in level.keys():
            l2.append(i[1])
    

        f2 = open('InputA.cpp')
        l3 = f2.read().splitlines()
        f2.close()
        
        l_final = []
        cnt = 0

        for line in l3:
            cnt += 1
            if cnt in l1:
                for i in l2:
                    if i in line:
                        l_final.append(i)
                        break
        
        temp = {}

        for i in level.keys():
            if i[1] not in l_final:
                continue
            j = (i[0],i[1])
            temp[j] = level[i]
        
        #print(level)
        #print(temp)
        return temp        

    def findResultantFunction(self,info):
        temp = []
        ans = []
        mn_lvl = 1000000000000 
        for i in info.keys():
            if info[i] < 2 :
                continue
            if info[i] < mn_lvl :
                mn_lvl = info[i]

        for i in info.keys():
            if info[i] == mn_lvl:
                temp.append(i[0])
                if i[1] not in ans:
                    ans.append(i[1])

        #print(temp)
        #print(ans)
        return ans,temp

    def updateFunctionName(self,dic,info,s):
        #print(dic)
        #print(info)
        temp = {}

        for i in info:
            f = (i[1])
            line_no = i[0]
            for i in dic.keys():
                if f in s[i]:
                    ll=[]
                    if f in temp.keys():
                        for x in temp[f]:
                            if x in ll:
                                continue
                            ll.append(x)
                    if line_no not in ll:
                        ll.append(line_no)
                    
                    temp[f] = ll

        #print(temp)

        return temp


    def gettingH3_h3(self,dic,info,ins,s,fn):

        mx = -1
        for i in info:
            if( 'main()' in s[i[0]]):
                continue
            if(i[1]>mx):
                mx = i[1]
        H3 = []
        h3 = []
        for i in info:
            if i[1] == mx:
                H3.append(i[0])

        for i in H3:
            a = i
            b = dic[i] + 1
            for j in range(a,b):
                if s[j] == '{' or s[j] == '}':
                    h3.append(j)
                    continue
                if j in ins:
                    h3.append(j)        
        
        temp = []
        #print(fn)
        for i in H3:
            for j in fn.keys():
                if j == self.utility.Function_DeclarationName(s[i]):
                    for x in fn[j]:
                        temp.append(x)
                 

        for i in temp:
            H3.append(i)
        #print(H3)
        #print(h3)
        return H3,h3

    def getAllHeuristicsAndHighlight(self, inputFileName , trackOfBlock, fn_name,strr):

        f2 = open(inputFileName)
        l2 = f2.read().splitlines()
        f2.close()
        fileName = "InputA.cpp"
        loop_temp = []
        ifelse_temp = []
        function_temp = []
        
        ins = []
        for line in l2:
            word = line.split()
            if word[0]=='line':
                ins.append(int(word[2]))
        
        #print('ins -> ')
        #print(ins)


        

        for line in l2:
            word = line.split()
            if word[0]=='line':
                temp = [0,int(word[2])]
                loop_temp.append(temp)
                ifelse_temp.append(temp)
                function_temp.append(temp)
                continue
            
            else:
                if (word[0] == 'loop_start_id'):
                    temp = [int(word[1]) , int(word[4])]
                    loop_temp.append(temp)
                    continue

                if (word[0] == 'loop_end_id'):
                    temp = [int(word[1]) , int(word[4])]
                    loop_temp.append(temp)
                    continue

                if (word[0] == 'ifelse_start_id'):
                    temp = [int(word[1]) , int(word[4])]
                    ifelse_temp.append(temp)
                    continue
                    
                if (word[0] == 'ifelse_end_id'):
                    temp = [int(word[1]) , int(word[4])]
                    ifelse_temp.append(temp)
                    continue

                if (word[0] == 'function_start_id'):
                    temp = [int(word[1]) , int(word[4])]
                    function_temp.append(temp)
                    continue
                    
                if (word[0] == 'function_end_id'):
                    temp = [int(word[1]) , int(word[4])]
                    function_temp.append(temp)
                    continue
    
        
        # --- ifElse Heuristics --- #
        
        if_dict = self.parenthesisBalance.IfTrackCalculation(trackOfBlock)
        else_dict = self.parenthesisBalance.ElseTrackCalculation(trackOfBlock)
        elseIf_dict = self.parenthesisBalance.ElseIfTrackCalculation(trackOfBlock)
        mergedIfElse = dict()
        mergedIfElse.update(if_dict)
        mergedIfElse.update(else_dict)
        mergedIfElse.update(elseIf_dict)
        

        ifelse_final = self.calculateStatementsForHeuristics(ifelse_temp)
        H1_IfElseifElse = self.getOptimalHeuristics(ifelse_final)
        H1_Sub = []
        for i in range(len(H1_IfElseifElse)):
            H1_IfElseifElse[i] -= 1
        #print(mergedIfElse)
        #print(H1_IfElseifElse) 
        #print(ifelse_final) 
        
        
        ifElseBit = {}
        for i in ifelse_final:
            if i[0] == -1 :
                continue
            a = i[1] - 1
            b = mergedIfElse[a]
            ifElseBit[(a,b)] = ifelse_final[i]

        
        for i in H1_IfElseifElse:
            a = i
            b = mergedIfElse[a] + 1
            for j in range(a,b):
                H1_Sub.append(j)
        
        # ------ Loop Terminating Branch ---- #
        loop_dict = self.parenthesisBalance.LoopTrackCalculation(trackOfBlock)
        loop_final = self.calculateStatementsForHeuristics(loop_temp)
        H2_Loop = self.getOptimalHeuristics(loop_final)
        H2_Sub = []
        for i in H2_Loop:
            a = i
            b = loop_dict[a] + 1
            for j in range(a,b):
                H2_Sub.append(j)

        loopBit = {}
        for i in loop_final:
            if i[0] != 1 :
                continue
            a = i[1]
            b = loop_dict[a]
            loopBit[(a,b)] = loop_final[i]   
        #print(loopBit)     


        # ------- Function Terminating Branch -----# 
        H3_Function = [] 
        H3_Sub = []
        function_dict = self.parenthesisBalance.FunctionTrackCalculation(trackOfBlock)
        function_final = self.calculateStatementsForHeuristics(function_temp)
        #print(fn_name)
        function_final = self.getFunctionStatement(function_final)
        fn_name = self.updateFunctionName(function_dict,fn_name,strr)
        H3_Function , H3_Sub = self.gettingH3_h3(function_dict,function_final,ins,strr,fn_name)
        
        funBit = {}
        for i in function_final:
            a = i[0]
            b = function_dict[a]
            if 'main()' in strr[a]:
                continue
            funBit[(a,b)] = i[1] 

        '''
        #function_level_cnt = self.calculateFunctioncallLevel( fn_name , loop_temp)
        #function_level_cnt = self.discardBuiltInFunction(function_level_cnt,function_dict)
        #function_ans , H3_Function = self.findResultantFunction(function_level_cnt)
        #H3_Function = self.findFunctionDefinition(fileName, function_ans , H3_Function,function_dict)        
        for i in H3_Function:
            if strr[i].startswith('return'):
                continue
            name = self.utility.Function_CallName(strr[i])
            for j in function_dict.keys():
                if name in strr[j] :
                    for k in range(j,function_dict[j]+1):
                        H3_Sub.append(k)
        '''
        self.highlightHeuristics.highlightingHeuristics(fileName,H1_IfElseifElse,H1_Sub,H2_Loop,H2_Sub,H3_Function,H3_Sub,"Heuristicts.html")
        return ifElseBit,loopBit,funBit

def main():
    obj = Detect_Sensitive_Code("test.c")

if __name__ == '__main__':
    main()