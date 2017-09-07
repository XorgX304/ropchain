from gadgets import util, gadget
from gadgets.asm import neg, dec, add
import ropchain

def find(reg, gadgets, canUse):
    rop = util.optROPChain(gadget.find(gadgets, 'inc', reg))
    rop = util.optMap(rop, fromNegDec, reg, gadgets, canUse)
    rop = util.optMap(rop, fromLeaPlusOne, reg, gadgets, canUse)
    rop = util.optMap(rop, fromAddOne, reg, gadgets)
    return rop

def fromNegDec(reg, gadgets, canUse):
    _neg = neg.find(reg, gadgets, canUse)
    _dec = dec.find(reg, gadgets, canUse)
    if _neg != None and _dec != None:
        return ropchain.ROPChain([_neg, _dec, _dec, _neg])
    else:
        return None

def fromAddOne(reg, gadgets, canUse):
    addOne = add.find(reg, '0x1', gadgets)
    if addOne != None:
        return ropchain.ROPChain(addOne)
    else:
        return None


def fromLeaPlusOne(reg, gadgets, canUse):
    for r in canUse:
        _lea = lea.find(reg, '[%s+0x1]' % r, gadgets, canUse)
        _mov = mov.find(r, reg, gadgets, canUse - set([r]))
        if _lea != None and _mov != None:
            return ropchain.ROPChain([_lea, _mov])
    return None