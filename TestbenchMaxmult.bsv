//Author: Bharati.K
//IIITDM, Kaceepuram
//Systolic Matrix Multiplication
//June, 2018

package TestbenchMaxmult;

//This program is for multiplying two square matrices of order of MAT_ORDER
//We assume the matrices are stored in row major order and fed by the Testbench
//into the design in the same way. NUM_ELEMENTS is the square of MAT_ORDER.
//Let C= A*B be the three matrices involved.

typedef 3 MAT_ORDER;
typedef 9 NUM_ELEMENTS;

// ================================================================
// Project Imports

import FIFO	:: *;
import moduleMaxmult	:: *;
import FIFOF     :: *;
import LFSR	:: *;
import Vector   :: *;
import StmtFSM  :: *;

(* synthesize *)

// ================================================================

module mkTestbench(Empty);
	IFC_type m <- mksystolicMaxMult();
	
	LFSR #(Bit #(32)) myrand <- mkLFSR_32;
	Reg#(int) count <- mkReg(0);
	Reg#(int) ele_count <- mkReg(0);
	Reg#(Bit #(32)) result <- mkReg(0);
	Reg#(Bool) disresult <- mkReg(False);

// (* descending_urgency = "row_load, col_load"*)
	
//This rule pushes random integers into the systolic architecture into rfifo
//Initialising the matrix A in row major order

rule row_load ( count < fromInteger(valueof(NUM_ELEMENTS)) );
	m.pushR(myrand.value()%8);	
	myrand.next();
	count <= count + 1;
endrule

//This rule pushes random integers into the systolic architecture into cfifo
//Initialising the matrix B in row major order

rule col_load ( (count >= fromInteger(valueof(NUM_ELEMENTS))) && (count < (2*fromInteger(valueof(NUM_ELEMENTS)))) );
	m.pushC(myrand.value()%8);	
	myrand.next();
	count <= count + 1;
endrule

//This rule waits till the matrix multiplication is completed and the
//final result is enqueued into ofifo.

rule proceed(!disresult);
	m.finishmult();
	disresult <= True;
endrule

//This rule extracts the content of the ofifos one by one to get matrix C in 
//row major order.

rule getresults(disresult);
	Bit#(32) data <- m.get(ele_count);
	$display("Ele_num: %d, Result: %d",ele_count, data);
	if(ele_count == fromInteger(valueof(NUM_ELEMENTS))-1) $finish;
	ele_count <= ele_count + 1;
endrule	
	
endmodule: mkTestbench


// ================================================================

endpackage: TestbenchMaxmult
