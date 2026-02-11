grammar G;

start
    : select_stmt
    ;

select_stmt
    : SELECT select_lst from_cl
    | SELECT select_lst from_cl where_cl
    ;


select_lst
    : id_lst
    | STAR
    ;


id_lst
    : id
    | id id_lst
    ;

from_cl : FROM tbl_lst;


tbl_lst
    : id_lst
    ;
where_cl : WHERE bcond;
bcond
    : bcond 'OR' bterm
    | bterm
    ;
    
bterm
    : bterm 'AND' bfactor
    | bfactor
    ;

bfactor
    : 'NOT' cond
    | cond
    ;
    
cond : value comp value;

value
    : id
    | str_lit
    | num
    ;

str_lit : '"' lit '"';


SELECT : 'SELECT';
FROM : 'FROM';
WHERE : 'WHERE';

STAR : '*';

fragment LIT : ('a' .. 'z')*;

COMP
    : '='
    | '<'
    | '>'
    | '<='
    | '>='
    | '!='
    ;

ID : [a-zA-Z0-9_]+;

NUM : [0-9]+;

lit : LIT;
id : ID;
num : NUM;
comp : COMP;

WS : (' '|'\n')+ -> skip;
