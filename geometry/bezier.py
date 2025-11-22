"""
Library for cubic Bézier curve generation and manipulation.
"""
import FreeCAD as App

def control_points(knots: list[App.Vector], closed: bool = False) -> list[tuple[App.Vector, App.Vector]]:
    """
    Control points for a smooth cubic Bézier spline passing through the given knots.
    
    Args:
        knots: A list of FreeCAD.Vector points to interpolate.
        closed: If True, the curve will be closed (smoothly connecting the last point back to the first).
                For closed curves, the first and last knots should NOT be identical in the input list.
                
    Returns:
        A list of tuples, where each tuple contains (control_point_1, control_point_2) for the
        corresponding segment.
    """
    n = len(knots)
    if n < 2:
        return []
    
    if closed:
        return _closed_control_points(knots)
    else:
        return _open_control_points(knots)

def _open_control_points(knots: list[App.Vector]) -> list[tuple[App.Vector, App.Vector]]:
    n = len(knots) - 1
    
    # Right hand side vector
    rhs = [App.Vector(0, 0, 0)] * n
    
    rhs[0] = knots[0] + 2 * knots[1]
    for i in range(1, n - 1):
        rhs[i] = 4 * knots[i] + 2 * knots[i+1]
    rhs[n-1] = 8 * knots[n-1] + knots[n]
    
    # First control points
    p1 = _thomas_algorithm(n, rhs)

    # Second control points
    p2 = [App.Vector(0, 0, 0)] * n
    for i in range(n - 1):
        p2[i] = 2 * knots[i+1] - p1[i+1]
    p2[n-1] = 0.5 * (knots[n] + p1[n-1])
    
    return list(zip(p1, p2))

def _thomas_algorithm(n: int, rhs: list[App.Vector]) -> list[App.Vector]:
    """
    Thomas algorithm for tridiagonal system specific to open spline.
    Matrix is:
    2 1 0 ...
    1 4 1 ...
    ... 1 4 1
    ... 0 2 7
    """
    # Matrix coefficients
    a = [1.0] * n # lower diag
    b = [4.0] * n # main diag
    c = [1.0] * n # upper diag
    
    b[0] = 2.0
    c[0] = 1.0
    
    a[n-1] = 2.0
    b[n-1] = 7.0
    c[n-1] = 0.0 
    
    # Forward elimination
    c_prime = [0.0] * n
    d_prime = [App.Vector(0,0,0)] * n
    
    c_prime[0] = c[0] / b[0]
    d_prime[0] = rhs[0] / b[0]
    
    for i in range(1, n):
        temp = b[i] - a[i] * c_prime[i-1]
        if i < n - 1:
            c_prime[i] = c[i] / temp
        d_prime[i] = (rhs[i] - a[i] * d_prime[i-1]) / temp
        
    # Back substitution
    p1 = [App.Vector(0,0,0)] * n
    p1[n-1] = d_prime[n-1]
    for i in range(n - 2, -1, -1):
        p1[i] = d_prime[i] - c_prime[i] * p1[i+1]
        
    return p1

def _closed_control_points(knots: list[App.Vector]) -> list[tuple[App.Vector, App.Vector]]:
    n = len(knots)
    rhs = [App.Vector(0,0,0)] * n
    for i in range(n):
        rhs[i] = 4 * knots[i] + 2 * knots[(i+1) % n]
        
    return _cyclic_algorithm(n, rhs, knots)

def _cyclic_algorithm(n: int, rhs: list[App.Vector], knots: list[App.Vector]) -> list[tuple[App.Vector, App.Vector]]:
    """
    Iterative solver for cyclic tridiagonal system.
    """
    p1 = list(knots) # Initial guess
    # 20 iterations is sufficient for convergence
    for _ in range(20):
        p1_new = [App.Vector(0,0,0)] * n
        for i in range(n):
            prev_p = p1[i-1] 
            next_p = p1[(i+1)%n]
            # 4*P1[i] + P1[i-1] + P1[i+1] = rhs[i]
            p1_new[i] = (rhs[i] - prev_p - next_p) * 0.25
        p1 = p1_new
        
    # Compute p2
    p2 = [App.Vector(0,0,0)] * n
    for i in range(n):
        p2[i] = 2 * knots[(i+1)%n] - p1[(i+1)%n]
        
    return list(zip(p1, p2))
