import Utility
import copy

class Highlight_Heuristics:
    utility = None

    def __init__(self):

        self.utility = Utility.Utility() 
        print("Successful Highlighting Heuristics")


    def getColorByRank(self, counter,H1,h1,H2,h2,H3,h3):
                if counter in H1:
                    curColor = "#9d0235"
                    burColor = "#7bc8ff"
                    return curColor,burColor

                if counter in H2:
                    curColor = "red"
                    burColor = "#5cffee"
                    return curColor,burColor

                if counter in H3:
                    curColor = "blue"
                    burColor = "#f6ff16"
                    return curColor,burColor

                if counter in h1:
                    curColor = "#9d0235"
                    burColor = "white"
                    return curColor,burColor

                if counter in h2:
                    curColor = "red"
                    burColor = "white"
                    return curColor,burColor

                if counter in h3:
                    curColor = "blue"
                    burColor = "white"
                    return curColor,burColor
                
                curColor = "black"
                burColor = "white"
                return curColor,burColor 
        
        
    def highlightingHeuristics(self, inputFileName,H1,h1,H2,h2,H3,h3,outputFileName):

        f3 = open(inputFileName)
        l3 = f3.read().splitlines()

        counter = 0
        stringfff = "<html><body><code>\n"
        for line in l3:

            counter = counter + 1

            if counter in range(1,4):
                continue

            if(line.startswith("#") or ('<' in line) or ('>' in line)):
                line = self.utility.Handeling_Html_Tag(line)

            if('freopen("Output.txt", "w+", stdout);' in line):
                line = '{'

            else:
                curColor , burColor = self.getColorByRank(counter,H1,h1,H2,h2,H3,h3)
            

            if curColor == "black":
                stringfff += '<p style="font-family:verdana;font-weight:bold;color:'+curColor+'">' + line + '</p>\n'
            else:
                stringfff += '<p style="font-family:verdana;font-size:20;font-weight:bold;background-color:'+burColor+';color:'+curColor+'">' + line +  '</p>\n'

        stringfff += "</code></body></html>\n"

    
        f3.close()
        f = open(outputFileName, "w")
        f.write(stringfff)
        f.close()








