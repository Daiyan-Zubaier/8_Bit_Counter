`default_nettype none
`timescale 1ns / 1ps

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a FST file
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  wire [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  tri [7:0] uio_pins;
  reg [7:0] external_data;
  reg [7:0] external_oe;
  assign uio_in = uio_pins;

  genvar i;
  generate
    for (i = 0; i < 8; i = i + 1) begin : pad_model
      assign uio_pins[i] = uio_oe[i] ? uio_out[i] : 1'bz; /*z = high imp output */
      assign uio_pins[i] = external_oe[i] ? external_data[i] : 1'bz;
    end
  endgenerate
`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  // Counter under test (or its netlist when GL_TEST is defined).
  tt_um_8_bit_counter_daiyan_zubaier user_project (

      // Include power ports for the Gate Level test:
`ifdef GL_TEST
      .VPWR(VPWR),
      .VGND(VGND),
`endif

      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

endmodule
