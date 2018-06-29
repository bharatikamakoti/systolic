#Python code for automatic bluespec code generation
#for recursive merge sort
#Author: Bharati. K
#IIITDM KAnceepuram
#June 2018
from math import log

#Number of elements to be sorted
NUM_ELEMENTS = 8 #change this parameter to vary number of elements.
#NUM_ELEMENTS MUST be a non-zero positive power of 2

# This function can be used to define a static variable 
def static_vars(**kwargs):
	def decorate(func):
		for k in kwargs:
			setattr(func,k,kwargs[k])
		return func
	return decorate
	
#3D arrays designating type, level and sublevel of different circuits.
inptype=[]
inplevel=[]
inpsublevel=[]

#There are three types of circuits, namely, swap (S), transform (T) 
#and combine (C).
#0 = 'I'; 1 = 'S'; 2 = 'C'; 3 = 'T'
circtype={0,1,2,3}

#The following 'for' loops convert the inptype, inplevel
#and inpsubelevel lists into 3D arrays.

for i in circtype:
        inptype.append([])
	for j in range(NUM_ELEMENTS):
		inptype[i].append([])
		for k in range(NUM_ELEMENTS):
			inptype[i][j].append('n')
		
for i in circtype:
        inplevel.append([])
	for j in range(NUM_ELEMENTS):
		inplevel[i].append([])
		for k in range(NUM_ELEMENTS):
			inplevel[i][j].append(-2)
			
for i in circtype:
        inpsublevel.append([])
	for j in range(NUM_ELEMENTS):
		inpsublevel[i].append([])
		for k in range(NUM_ELEMENTS):
			inpsublevel[i][j].append(-2)

#This function recursively sorts num elements stored 
#in an array starting from index p to p+num-1. It takes in four
#arguments p, num (as explained above), level (to track the pipelining in recursion)
#and dire (to track the data flow) - explained later.
	
def sort ( p, num, level,dire,doprint):
	if(num==1):
		return;
	else:
		sort(p, num/2, level+1,dire,doprint);
		sort(p+num/2, num/2, level+1,1,doprint);
		merge(p, num,level+1,0,dire,doprint);
		return;

#The following function recursively merges two sorted arrays 
#stored from p to p+num/2-1 and p+num/2 to p+num-1.
#It takes in five arguments: p, num, level, dire (as mentioned earlier)
#and sublevel (to track the pipelining in recursive merging).
#The recursive sort constructs the recursive tree that has two 
#calls to sort and one call to merge at each level. The sublevel variable
#tracks the level of the recursive merge called in each level of sorting.
#The data flows from the leaves of the recursive tree towards the root.
#At each stage, every data item is subjected to the same processing as every other 
#data item. So, if we track the processing involved in the leftmost path of the
#recursive tree, the same can be repeated for the items involved in other paths 
#by just changing the indices.
#Let us describe the sorting of four elements stored in a[0] to a[3].
#sort(0,4,0,0) -> sort(0,2,1,0) & sort(2,2,1,1) -> merge(0,4,1,0,0) 
#sort(0,2,1,0) -> sort(0,1,2,0) & sort(1,1,2,1) -> merge(0,2,2,0,0) 
#sort(2,2,1,1) -> sort(2,1,2,1) & sort(3,1,2,1) -> merge(2,2,2,0,1)
#merge(0,4,1,0,0) -> transform(0,4,1,0,0) -> merge(0,2,1,1,0) & merge(2,2,1,1,1) -> combine(0,4,1,0,0)
#The merge routine used is the odd-even merge, wherein, given two sorted sequences
#all the odd elements in both the sequences are taken together and recursively
#merged and all the even elements are taken together and recursively merged. The elements in the two
#odd and even sorted sequences are compared to give the combined merged sequence. The transform
#circuit is used for splitting the odd and even elements while the combine circuit is used for comparing the
#odd and even sorted sequences.
  
#In the above sorting of four elements, let us see the working of the elements involved in the left-most
#path of the recursive tree. These are the entries with dire argument equal to 0. 
#They are sort(0,4,0,0) that need to sort a[0] to a[3] ->sort(0,2,1,0) that need to sort a[0] 
#to a[2] -> sort(0,1,2,0) that need to sort a[0].
#op1: merge(0,2,2,0,0) that needs to merge a[0] to a[1] which is nothing but a swap operation.
#        This takes input from 'a' array and gives output to s3[0] and s3[1] in the s3 array.
#op2: merge(0,4,1,1,0) that needs to merge the output of op1, takes the two sorted sequences
#	   (s3[0], s3[1]) and (s3[2], s3[3]) and transforms it to (t1[0], t1[1]) and (t1[2], t1[3]). At the beginning 
#	   of op2, the sorted array (s3[2], s3[3]) is made available by merge(2,2,2,0,1) which is nothing but 
#	   op1 happening on a[2] and a[3] in parallel with op1 happening on a[0] and a[1].
#op3: Takes the output of t1 array and does the combine to yield the final sorted sequence in c1 array.
#So the data moves from arrays a -> s3 -> t1 -> c1 with op1, op2 and op3 as respective operations in between.
#This achieves the required pipelining. When first set of data is in c1, the second set of data is in t1, the third set of #data is in s3 and the fourth set of data is in a.

#In the routine, pmodu , plevel and psublevel indicates the most recent operation(S,C,T) that happened
#on the explored element in the left-most path. In the Bluespec code, the output of that operation is to be stored 
#in the Vector named concat (pmodu, plevel, psublevel ). This will feed as the input to the next operation of
#the next explored element of the left-most path. Hence, these values have to be remembered across iterations.
#Hence, they are made static variables.

@static_vars(pmodu = 'a')
@static_vars(plevel = 0)
@static_vars(psublevel = 0)
def merge( p,  num, level, sublevel,dire,doprint):
	if(num==2): #swap
		
		if (dire == 0):
			inptype[1][level][sublevel] = merge.pmodu
			inplevel[1][level][sublevel] = merge.plevel
			inpsublevel[1][level][sublevel] = merge.psublevel
			merge.pmodu = 's'
			merge.plevel = level
			merge.psublevel = sublevel
		if(doprint==1):
			f1.write( "// Swap: %d %d %d %d %c %d %d\n" % (p, num, level, sublevel, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel]));
			f1.write( "if (%c%d%d[%d] > %c%d%d[%d]) begin\n" % (inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p+1))
			f1.write( "  s%d%d[%d] <= %c%d%d[%d];\n" % (level, sublevel, p, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p+1))
	        	f1.write( "  s%d%d[%d] <= %c%d%d[%d]; end\n" % (level, sublevel, p+1, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p))	
	        	f1.write( "else begin\n")
	        	f1.write( "  s%d%d[%d] <= %c%d%d[%d];\n" % (level, sublevel, p, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p))
	        	f1.write( "  s%d%d[%d] <= %c%d%d[%d]; end\n" % (level, sublevel, p+1, inptype[1][level][sublevel], inplevel[1][level][sublevel], inpsublevel[1][level][sublevel], p+1))
	        
		return;
	else:
		
		if (dire == 0): #transform
			inptype[3][level][sublevel] = merge.pmodu
			inplevel[3][level][sublevel] = merge.plevel
			inpsublevel[3][level][sublevel] = merge.psublevel
			merge.pmodu = 't'
			merge.plevel = level
			merge.psublevel = sublevel
			
		if(doprint==1):
			f1.write( "// Transform: %d %d %d %d %c %d %d\n" % (p, num, level, sublevel, inptype[3][level][sublevel], inplevel[3][level][sublevel], inpsublevel[3][level][sublevel]));
			f1.write( "for ( Int#(32) i=0; i< %d; i=i+1) begin\n" % (num/2))
			f1.write( "  t%d%d[%d+i] <= %c%d%d[%d+2*i];\n" % (level, sublevel, p, inptype[3][level][sublevel], inplevel[3][level][sublevel], inpsublevel[3][level][sublevel], p))
	        	f1.write( "  t%d%d[%d+i] <= %c%d%d[%d+2*i]; end\n" % (level, sublevel, p+num/2, inptype[3][level][sublevel], inplevel[3][level][sublevel], inpsublevel[3][level][sublevel], p+1))
	        		
		merge(p, num/2, level, sublevel+1,dire,doprint);
		merge(p+num/2, num/2, level, sublevel+1,1,doprint);
		
		
		if (dire == 0):#combine
			inptype[2][level][sublevel] = merge.pmodu
			inplevel[2][level][sublevel] = merge.plevel
			inpsublevel[2][level][sublevel] = merge.psublevel
			merge.pmodu = 'c'
			merge.plevel = level
			merge.psublevel = sublevel
		if(doprint==1):
			f1.write( "// Combine: %d %d %d %d %c %d %d\n" % (p, num, level, sublevel, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel]))
			f1.write( "for (Int #(32) i=1; i< %d; i=i+1) begin\n" % (num/2))
			f1.write( "  c%d%d[%d+2*i] <= (%c%d%d[%d+i] < %c%d%d[%d+i]) ? %c%d%d[%d+i] : %c%d%d[%d+i];\n" % (level, sublevel, p-1, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p+num/2-1, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p+num/2-1))
			f1.write( "  c%d%d[%d+2*i] <= (%c%d%d[%d+i] >= %c%d%d[%d+i]) ? %c%d%d[%d+i] : %c%d%d[%d+i]; end\n" % (level, sublevel, p, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p+num/2-1, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p, inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p+num/2-1))
			f1.write( "c%d%d[%d] <= %c%d%d[%d];\n" % (level, sublevel, p,  inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p))
			f1.write( "c%d%d[%d] <= %c%d%d[%d];\n" % (level, sublevel, p+num-1,  inptype[2][level][sublevel], inplevel[2][level][sublevel], inpsublevel[2][level][sublevel], p+num-1))
		
		return

f1= open("moduleOEMS.bsv","w")
f1.write("//Odd-Even Merge Sort\n")
f1.write("//Systolic Recursive Tree Architecture\n")
f1.write("//Author: K.Bharati, IIITDM KANCEEPURAM\n")
f1.write("//Date: June 2018\n")
f1.write("package moduleOEMS;\n")
f1.write("// ================================================================\n")
f1.write("// Project imports\n")
f1.write("import Vector         :: *;\n")
f1.write("typedef %d NUM_ELEMENTS;\n"% (NUM_ELEMENTS))
f1.write("// ================================================================\n")
f1.write("// Interface for the Odd-Even Merge sort module\n")
f1.write("interface OEMSort_IFC;\n")
f1.write("   method Action start( Int#(32) j);\n")
f1.write("   method Action finishload();\n")
f1.write("   method Action completesort();\n")
f1.write("   method int getsortvalue();\n")
f1.write("endinterface\n")
f1.write("(* synthesize *)\n")
f1.write("module mkOEMsort (OEMSort_IFC);\n")
f1.write("//For the proposed parallel sorting algorithm\n")
f1.write("//We can use a step counter. For a fact, we know that given N elements, the sort takes\n")
f1.write("//place in atmost in (log N)*(log N) steps\n")
f1.write("	//This register holds the number of processing steps done at any instance, max of which is (log N)^2 \n")
f1.write("	Reg#(Int#(32)) rg_sc <- mkReg (0);\n")
f1.write("  	Vector#(NUM_ELEMENTS,Reg#(Int#(32))) a00 <- replicateM( mkRegU );\n")
f1.write("        Reg#(Int#(32)) step <- mkReg(1);\n")

sort(0, NUM_ELEMENTS, 0,0,0);

d1 = {'i': 0, 's':1, 'c':2, 't':3, 'n':-1, 'a':-1}
for i in circtype:
	for j in range(NUM_ELEMENTS):
		for k in range(NUM_ELEMENTS):
			if d1[inptype[i][j][k]] > 0:
			 		f1.write( "Vector#(%d, Reg#(Int #(32))) %c%d%d <- replicateM ( mkReg(0) );\n" % (NUM_ELEMENTS, inptype[i][j][k], inplevel[i][j][k], inpsublevel[i][j][k]))
f1.write(  "Vector#(%d, Reg#(Int #(32))) %c%d%d <- replicateM ( mkReg(0) );\n" % (NUM_ELEMENTS, merge.pmodu, merge.plevel, merge.psublevel))	
f1.write("// ================================================================\n")
f1.write("// Rules\n")
f1.write("// After step 1, the Odd-even Merge Sort starts\n")
f1.write("// At every step, the rg_sc is incremented which helps in\n")
f1.write("// identifying the end of all steps.\n")
f1.write("rule inc_count ( (step == 2) && (rg_sc < %d) );\n" % ( (log(NUM_ELEMENTS)/log(2))*(log(NUM_ELEMENTS)/log(2)) )  )
f1.write("	rg_sc <= rg_sc + 1;\n")
f1.write("endrule\n")
f1.write("rule startsort (step==2);\n")

merge.pmodu='a'
merge.plevel=0
merge.psublevel=0
sort(0, NUM_ELEMENTS, 0,0,1);

f1.write("endrule\n")
f1.write("rule swap_out (step == 3);\n")
f1.write("	 for (Int#(32) k = 0; k < fromInteger(valueof(NUM_ELEMENTS))-1; k = k+1)\n")
f1.write("             %c%d%d[k] <= %c%d%d[k+1];\n" % (merge.pmodu, merge.plevel, merge.psublevel,merge.pmodu, merge.plevel, merge.psublevel))
f1.write("endrule\n")
f1.write("// ================================================================\n")
f1.write("// Interfaces\n")
f1.write("//The start method is called NUM_ELEMENTS times by the Tb\n")
f1.write("//Each time, it accepts an integer and shifts it into the systolic array\n")
f1.write("   method Action start(Int#(32) j) if (step==1); \n")
f1.write("        a00[0] <= j; \n")
f1.write("        for (Int#(32) k = 0; k < fromInteger(valueof(NUM_ELEMENTS))-1; k = k+1)\n")
f1.write("             a00[k+1] <= a00[k];\n")
f1.write("   endmethod\n")
f1.write(" //This method is triggered by the Tb when the last element of A00\n")
f1.write(" //is loaded into the 1D systolic array\n")
f1.write("    method Action finishload();\n")
f1.write("         step <= 2;\n")
f1.write("        endmethod\n")
f1.write("   method Action completesort() if(rg_sc==%d);\n" % ( (log(NUM_ELEMENTS)/log(2))*(log(NUM_ELEMENTS)/log(2)) )  )
f1.write("    	step <= 3;\n")
f1.write("    endmethod\n")
f1.write("   method int getsortvalue();\n")
f1.write("    	return %c%d%d[0];\n" % (merge.pmodu, merge.plevel, merge.psublevel))
f1.write("    endmethod\n")
f1.write("endmodule: mkOEMsort\n")
f1.write("// ================================================================\n")
f1.write("endpackage: moduleOEMS\n")
f1.close()

#Testbench
f=open("TestbenchOEMS.bsv", "w")
f.write("package TestbenchOEMS;\n")
f.write( "// ===============================================================\n")
f.write("import moduleOEMS     :: *;\n")
f.write( "import LFSR           :: *;\n")
f.write( "import Vector		:: *;\n")
f.write(" typedef %d NUM_ELEMENTS;\n"% (NUM_ELEMENTS))
f.write("(* synthesize *)\n")
f.write("module mkTestbench (Empty); //Empty since it is the top module\n")
f.write("	OEMSort_IFC m <- mkOEMsort ();\n")
f.write("LFSR #(Bit #(32)) myrand <- mkLFSR_32;\n")
f.write("Vector #(NUM_ELEMENTS,Reg#(Int#(32))) inp_arr <- replicateM(mkRegU);\n")
f.write("Vector #(NUM_ELEMENTS,Reg#(Int#(32))) out_arr <- replicateM(mkRegU);\n")
f.write("Reg#(Bool) mystart <- mkReg(False);\n")
f.write("Reg#(Int#(32)) count <- mkReg(0);\n")
f.write("Reg#(Bool) myFinish <- mkReg(False);\n")
f.write("Reg#(Bool) myPrint <- mkReg(False);\n")
f.write("(* descending_urgency = \"rl_inp, r1_go, rl_finish, rl_dump, rl_print \"*)\n")
f.write("//This rule assigns the values for inp_arr and makes mystart <= True.\n")
f.write("rule rl_inp( !mystart);\n")
f.write("	inp_arr[0] <= unpack(myrand.value()); \n")
f.write("	myrand.next();\n")
f.write("	mystart <= True;\n")
f.write("endrule\n")
f.write("//This rule starts after rl_inp. It pushes the inp_arr values one by one \n")
f.write("//into the 1D systolic array and while pushing the last element, it triggers\n")
f.write("//the finishload method indicating to the 1D array that it has finished loading.\n")
f.write("rule r1_go ( (mystart) && (count < fromInteger(valueof(NUM_ELEMENTS))));\n")
f.write("	m.start(inp_arr[count]);\n")
f.write("	inp_arr[count+1] <= unpack(myrand.value());\n")
f.write("	myrand.next();\n")
f.write("	count <= count + 1;\n")
f.write("	if (count == fromInteger(valueof(NUM_ELEMENTS))-1) m.finishload();\n")
f.write("endrule\n")
f.write("rule rl_finish(!myFinish);\n")
f.write("	m.completesort();\n")
f.write("	$display(\"The unsorted sequence is : \");\n")
f.write("	for(Integer i=0; i < fromInteger (valueof(NUM_ELEMENTS)); i=i+1)\n")
f.write("		$display (\"%d \",inp_arr[i]);\n") 
f.write("	myFinish <= True;\n")
f.write("	count <=0;\n")
f.write("endrule\n")
f.write("rule rl_dump ( (myFinish) && (count < fromInteger(valueof(NUM_ELEMENTS))));\n")
f.write("	out_arr[count] <= m.getsortvalue();\n")
f.write("	count <= count + 1;\n")
f.write("	if (count == fromInteger(valueof(NUM_ELEMENTS))-1) myPrint <= True;\n")
f.write("endrule\n")
f.write("rule rl_print (myPrint);\n")
f.write("	$display(\"The Sorted sequence is : \");\n")
f.write("	for(Integer i=0; i < fromInteger (valueof(NUM_ELEMENTS)); i=i+1)\n")
f.write("		$display (\"%d \",out_arr[i]);\n") 
f.write("	$finish;\n")
f.write("endrule\n")
f.write("endmodule: mkTestbench\n")
f.write("endpackage: TestbenchOEMS\n")
f.close()












