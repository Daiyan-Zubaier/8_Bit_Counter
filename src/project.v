/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_8_bit_counter_daiyan_zubaier (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
  reg[7:0] counter;

  wire load_en = ui_in[0];
  wire control_en = ui_in[1];

  always @(posedge clk or negedge rst_n) begin
    if (rst_n == 0) begin
      counter <= 8'b0;
    end else if (load_en) begin
      counter <= uio_in;
    end else begin
      counter <= counter + 8'b00000001;
    end
  end

  assign uio_out = counter;
  assign uio_oe = {8{control_en}};

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, 1'b0, uo_out};
  assign uo_out = 8'b0;
endmodule
