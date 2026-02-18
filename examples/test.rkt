; (x y (z 1))
; (: x [X Y] (X Y -> Integer))
(define (x) (lambda (x y) (+ x y))