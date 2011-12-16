from functools import partial

from migen.fhdl import structure as f

class Inst:
	def __init__(self, w):
		self.w = w
		
		d = partial(f.declare_signal, self)
		
		d("start_i")
		d("dividend_i", f.BV(w))
		d("divisor_i", f.BV(w))
		d("ready_o")
		d("quotient_o", f.BV(w))
		d("remainder_o", f.BV(w))
		
		d("_qr", f.BV(2*w))
		d("_counter", f.BV(f.bits_for(w)))
		d("_divisor_r", f.BV(w))
		d("_diff", f.BV(w+1))
	
	def get_fragment(self):
		a = f.Assign
		comb = [
			a(self.quotient_o, self._qr[:self.w]),
			a(self.remainder_o, self._qr[self.w:]),
			a(self.ready_o, self._counter == f.Constant(0, self._counter.bv)),
			a(self._diff, self.remainder_o - self._divisor_r)
		]
		sync = [
			f.If(self.start_i == 1, [
				a(self._counter, self.w),
				a(self._qr, self.dividend_i),
				a(self._divisor_r, self.divisor_i)
			], [
				f.If(self.ready_o == 0, [
					f.If(self._diff[self.w] == 1,
						[a(self._qr, f.Cat(0, self._qr[:2*self.w-1]))],
						[a(self._qr, f.Cat(1, self._qr[:self.w-1], self._diff[:self.w]))]),
					a(self._counter, self._counter - f.Constant(1, self._counter.bv)),
				])
			])
		]
		return f.Fragment(comb, sync)
