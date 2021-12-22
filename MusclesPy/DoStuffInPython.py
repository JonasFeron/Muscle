import sys
import data as d
import result as r

#0) retrieve inputted_data

#example
#when we run in the terminal:
#python DoStuffInPython.py arg1 arg2 arg3
#this lauch DoStuffInPython.py
#with the sys.argv = list [DoStuffInPython.py, arg1, arg2, arg3]


def main():
    key = sys.argv[1] #the GuID
    dataPath = sys.argv[2] #retrieve arg1 sent by C# as an inputted_data
    (keyInTxtFile,DataStr) = d.ReadDataFile(dataPath)
    output_str=" "
    if (key  == keyInTxtFile):
        try:
            result0 = DataStr[0].lower()  # Do stuff in python
            result1 = DataStr[1].upper()  # Do stuff in python
            output_str = result0[:len(result0)-1] + " " + result1[:len(result1)-1]
        except Exception as e:
            output_str = str(e)
    else:
        output_str = "Keys from command prompt and Data text file did not match"
    resultPath = r.WriteResultFile(dataPath, r.FileTestResult, key, output_str)
    print(key + ":" + resultPath)


if __name__ == '__main__': #what happens if called from C#
    main()