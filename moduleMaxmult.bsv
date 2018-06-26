//Author: Bharati.K
//IIITDM, Kaceepuram
//Systolic Matrix Multiplication
//June, 2018

package moduleMaxmult;

//This program is for multiplying two square matrices of order of MAT_ORDER
//We assume the matrices are stored in row major order and fed by the Testbench
//into the design in the same way. NUM_ELEMENTS is the square of MAT_ORDER.
//Let C= A*B be the three matrices involved.

typedef 3 MAT_ORDER;
typedef 9 NUM_ELEMENTS;

// ================================================================
// Project Imports

import FIFO	:: *;
import FIFOF     :: *;
import LFSR	:: *;
import Vector   :: *;
import StmtFSM  :: *;

// ================================================================
	
interface IFC_type;
	method Action pushR(Bit #(32) a);
	method Action pushC(Bit #(32) a);
	method Action finishmult();
	method ActionValue#(Bit #(32)) get(Int# (32) a);
endinterface: IFC_type

// ================================================================

(* synthesize *)

module mksystolicMaxMult(IFC_type);

//There are MAT_ORDER number of rfifos and cfifos
//that are used for storing matrix A and matrix B respectively
//ith row of A will be stored in rfifo[i]
//ith column of B will be stored in cfifo[i]
//ith row of C will be stored in ofifo[i]

Vector#( MAT_ORDER, FIFO#(Bit#(32)) ) rfifo <- replicateM ( mkSizedFIFO(valueof(MAT_ORDER)) );
Vector#( MAT_ORDER, FIFO#(Bit#(32)) ) cfifo <- replicateM ( mkSizedFIFO(valueof(MAT_ORDER)) );
Vector#( MAT_ORDER, FIFOF#(Bit#(32)) ) ofifo <- replicateM ( mkSizedFIFOF(valueof(MAT_ORDER)) );


Reg#(Int #(32)) row_loadcount <- mkReg(0);
Reg#(Int #(32)) col_loadcount <- mkReg(0);
Reg#(Bool) finishload <- mkReg(False);
Reg#(Int #(32)) mult_count <- mkReg(0);
Reg#(Bool) resultload <- mkReg(False);
Reg#(Bit #(32)) temp <- mkReg(0);

//A computational element in the systolic array will have an accumalator "sum"
//A vertical input from the top "vert" and a horizontal input from left "horiz"
//We have used single dimensional arrays of size NUM_ELEMENTS to capture this
//(i,j) --> i*MAT_ORDER + j

Vector#( NUM_ELEMENTS, Reg#(Int# (32)) ) vert <- replicateM (mkReg(0));
Vector#( NUM_ELEMENTS, Reg#(Int# (32)) ) horiz <- replicateM (mkReg(0));
Vector#( NUM_ELEMENTS, Reg#(Int# (32)) ) sum <- replicateM (mkReg(0));

(* descending_urgency = "pushR, pushC, startmult, resultqueue, get" *)

//The element (i,j) works in the cycle between (i+j) and (i+j+ MAT_ORDER-1)
//The following rule is fired after the input matrices are loaded into rfifo and cfifo

rule startmult( finishload && !resultload );
	for( Int #(32) i=0; i< fromInteger(valueof(MAT_ORDER)); i=i+1) 
		for( Int #(32) j=0; j< fromInteger(valueof(MAT_ORDER)); j=j+1)
		if((mult_count >= (i+j)) && (mult_count <= (i+j-1 + fromInteger(valueof(MAT_ORDER))))) begin
			if(i==0 && j==0) begin //(0,0) element takes from rfifo and cfifo
				sum[i*fromInteger(valueof(MAT_ORDER))+j] <= sum[i*fromInteger(valueof(MAT_ORDER))+j] + unpack(rfifo[i].first())*unpack(cfifo[j].first()); 
				horiz[i*fromInteger(valueof(MAT_ORDER))+j] <= unpack(rfifo[i].first());
				vert[i*fromInteger(valueof(MAT_ORDER))+j] <= unpack(cfifo[j].first());
				rfifo[i].deq();
				cfifo[j].deq();
			end
		
			if(i==0 && j>0) begin //(0,j) elements take from (0,j-1) and cfifo
				sum[i*fromInteger(valueof(MAT_ORDER))+j] <= sum[i*fromInteger(valueof(MAT_ORDER))+j] + horiz[i*fromInteger(valueof(MAT_ORDER))+(j-1)]*unpack(cfifo[j].first()); 
				horiz[i*fromInteger(valueof(MAT_ORDER))+j] <= horiz[i*fromInteger(valueof(MAT_ORDER))+(j-1)];
				vert[i*fromInteger(valueof(MAT_ORDER))+j] <= unpack(cfifo[j].first());
				cfifo[j].deq();
			end
		
			if(i>0 && j==0) begin //(i,0) elements take from rfifo and (i-1,0)
				sum[i*fromInteger(valueof(MAT_ORDER))+j] <= sum[i*fromInteger(valueof(MAT_ORDER))+j] + vert[(i-1)*fromInteger(valueof(MAT_ORDER))+j]*unpack(rfifo[i].first()); 
				vert[i*fromInteger(valueof(MAT_ORDER))+j] <= vert[(i-1)*fromInteger(valueof(MAT_ORDER))+j];
				horiz[i*fromInteger(valueof(MAT_ORDER))+j] <= unpack(rfifo[i].first());
				rfifo[i].deq();
			end
			
			if(i>0 && j>0) begin//(i,j) elements take from (i,j-1) and (i-1,j)
				sum[i*fromInteger(valueof(MAT_ORDER))+j] <= sum[i*fromInteger(valueof(MAT_ORDER))+j] + horiz[i*fromInteger(valueof(MAT_ORDER))+(j-1)]*vert[(i-1)*fromInteger(valueof(MAT_ORDER))+j]; 
				horiz[i*fromInteger(valueof(MAT_ORDER))+j] <= horiz[i*fromInteger(valueof(MAT_ORDER))+(j-1)];
				vert[i*fromInteger(valueof(MAT_ORDER))+j] <= vert[(i-1)*fromInteger(valueof(MAT_ORDER))+j];
			end
		
		
		end
endrule

//This rule is fired after multplication is completed and the result is available in Vector "sum".
//This rule pushes the sum vector into ofifo[i]: (0 <= i < MAT_ORDER) such that the row i of the resultant matrix 
//is stored in ofifo[i]

rule resultqueue ((resultload == True)  && (mult_count <= 3* fromInteger(valueof(MAT_ORDER))-3 + fromInteger(valueof(MAT_ORDER))));

	for(Int #(32) i=0; i< fromInteger(valueof(MAT_ORDER)); i=i+1 ) begin
               ofifo[i].enq(pack(sum[i*fromInteger(valueof(MAT_ORDER))]));
                 $display("Rqueue Loading at cycle %d, fifo %d, value %d", mult_count, i, sum[i*fromInteger(valueof(MAT_ORDER))]);
		for(Int #(32) j=0; j< fromInteger(valueof(MAT_ORDER)) - 1; j=j+1 ) begin
		        sum[i*fromInteger(valueof(MAT_ORDER))+j] <= sum[i*fromInteger(valueof(MAT_ORDER))+(j+1)]; 
		end
		end
		
endrule

//This rule is fired after the input matrices are loaded into rfifo and cfifo
//After that point, the rule keeps track of the mult_count.
//This is important because (i,j)th element needs to work between (i+j) and (i+j+MAT_ORDER-1) mult cycles
//The rule also enables resultload when the multiplication finishes and the results are available in Vector "sum" 

rule inc_multcount(finishload);
	mult_count <= mult_count + 1;
	if (mult_count == (3* fromInteger(valueof(MAT_ORDER)) - 3) ) begin
		resultload <= True;
		end
endrule

//This method enqueues matrix A elements one by one into the rfifos such that row i of A 
//is enqueued into rfifo[i]
 
method Action pushR(Bit #(32) a);
	rfifo[row_loadcount/fromInteger(valueof(MAT_ORDER))].enq(a);
	row_loadcount <= row_loadcount + 1;
	$display("Row count = %d, value = %d", row_loadcount, a);
endmethod

//This method enqueues elements of matrix B one by one into the cfifos such that column i of B
//is enqueued into cfifo[i]

method Action pushC(Bit# (32) a);
	cfifo[col_loadcount%fromInteger(valueof(MAT_ORDER))].enq(a);
	col_loadcount <= col_loadcount + 1;
	$display("Column count = %d, value = %d", col_loadcount, a);
	if( col_loadcount == fromInteger(valueof(NUM_ELEMENTS))-1)
		finishload <= True;
endmethod

//This method is fired after the resultant matrix C is stored on ofifo. 
//This intimates to the Testbench that the result is ready

method Action finishmult() if( mult_count == (3*fromInteger(valueof(MAT_ORDER)) - 3 + fromInteger(valueof(MAT_ORDER))) );
	let temp_load = True; //dummy action
endmethod

//This method is used by the Testbench to extract the C matrix in row major order one by one
//As the resultant matrix is stored in row major order in the ofifos
//such that ofifo[i] stores row i of the resultant matrix, the testbench calls this method such that
//the method dequeues all elements of ofifo[0], one each per call followed by all elements of ofifo[1] and so on.  

method ActionValue#(Bit #(32)) get(Int# (32) a) if( mult_count > (3*fromInteger(valueof(MAT_ORDER)) - 3 + fromInteger(valueof(MAT_ORDER))) );

	let data = ofifo[a/fromInteger(valueof(MAT_ORDER))].first();
	if (a%fromInteger(valueof(MAT_ORDER)) < fromInteger(valueof(MAT_ORDER))-1) //PROBLEM: The last element of ofifo[i], if dequeued, hangs.
	    ofifo[a/fromInteger(valueof(MAT_ORDER))].deq();
	$display("I am here with A = %d temp = %d fifo = %d cycle %d", a, data, a/fromInteger(valueof(MAT_ORDER)),mult_count);
	return data;
endmethod

endmodule: mksystolicMaxMult

// ================================================================

endpackage: moduleMaxmult
