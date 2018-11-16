function inv = getInv(s)

global b0 N

b = getBoolean(s);
e = sum(abs(b0-b));
inv = (N-e < e);

    