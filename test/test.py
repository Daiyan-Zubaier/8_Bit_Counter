# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly, Timer


async def settle():
    # Allow propagation time for gate-level simulation as well as RTL updates
    await Timer(1, unit="us")
    await ReadOnly()


async def setup(dut):
    """Start each test with its own clock and a reset counter."""
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.external_data.value = 0
    dut.external_oe.value = 0
    dut.rst_n.value = 0
    clock = Clock(dut.clk, 100, unit="ms") # 10 hz
    cocotb.start_soon(clock.start())

    await ClockCycles(dut.clk, 2)
    await settle()
    assert dut.uio_out.value == 0
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1


@cocotb.test()
async def test_load(dut):
    await setup(dut)
    previous = 0

    for value in range(256):
        dut.external_data.value = value
        dut.external_oe.value = 0xFF
        dut.ui_in.value = 0b01
        await settle()
        assert dut.uio_in.value == value
        assert dut.uio_oe.value == 0

        assert dut.uio_out.value == previous

        await ClockCycles(dut.clk, 1)
        await settle()
        assert dut.uio_out.value == value
        previous = value
        await FallingEdge(dut.clk)

    dut.external_oe.value = 0
    dut.ui_in.value = 0b10
    await settle()
    assert dut.uio_pins.value == 255
    await ClockCycles(dut.clk, 1)
    await settle()
    assert dut.uio_pins.value == 0


@cocotb.test()
async def test_counter_increment(dut):
    await setup(dut)
    dut.ui_in.value = 0b10

    for i in range(1, 257):
        await ClockCycles(dut.clk, 1)
        await settle()
        assert dut.uio_out.value == (i % 256)
        assert dut.uio_pins.value == (i % 256)
        assert dut.uio_oe.value == 0xFF


@cocotb.test()
async def test_high_impedance(dut):
    await setup(dut)
    dut.ui_in.value = 0b10
    await settle()
    assert dut.uio_oe.value == 0xFF
    assert dut.uio_pins.value == 0

    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b00
    await settle()
    assert dut.uio_oe.value == 0
    assert str(dut.uio_pins.value).lower() == "zzzzzzzz"

    for i in range(1, 257):
        await ClockCycles(dut.clk, 1)
        await settle()
        assert dut.uio_out.value == ((1 + i) % 256)
        assert dut.uio_oe.value == 0
        assert str(dut.uio_pins.value).lower() == "zzzzzzzz"

    await FallingEdge(dut.clk)
    dut.ui_in.value = 0b10
    await settle()
    assert dut.uio_oe.value == 0xFF
    assert dut.uio_pins.value == 1


@cocotb.test()
async def test_async_reset(dut):
    await setup(dut)
    await ClockCycles(dut.clk, 3)
    await settle()
    assert dut.uio_out.value == 3

    await FallingEdge(dut.clk)
    dut.external_data.value = 42
    dut.external_oe.value = 0xFF
    dut.ui_in.value = 0b01
    dut.rst_n.value = 0
    await settle()
    assert dut.uio_out.value == 0 

    await ClockCycles(dut.clk, 1)
    await settle()
    assert dut.uio_out.value == 0

    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    await settle()
    assert dut.uio_out.value == 42
