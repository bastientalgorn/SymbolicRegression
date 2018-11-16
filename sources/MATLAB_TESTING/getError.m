function e = getError(s)

global b0 N count

count = count+1;
b = getBoolean(s);
e = sum(abs(b0-b));
e = min(e,N-e);

    