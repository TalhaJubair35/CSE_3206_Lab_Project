#!/usr/bin/env python3
"""
===============================================================================
                         SUPER CALCULATOR - CSE 3206
                          Student ID: 2203036
===============================================================================
A feature-rich, high-performance, and versatile Calculator application.
Features:
 - Safe AST-based Expression Evaluator (Infix math, functions, constants)
 - Scientific & Combinatorics Module (Trigonometry, Factorials, nPr, nCr, GCD/LCM)
 - Statistical Analysis (Mean, Median, Mode, Variance, Std Dev, Range)
 - Financial Tools (Simple & Compound Interest, EMI Calculator)
 - Base & Bitwise Converter (Dec/Bin/Oct/Hex & Bitwise operations)
 - Multi-Unit Converter (Length, Mass, Temperature, Data Storage)
 - Solvers & Matrix Operations (Quadratic, Linear Systems, 2x2/3x3 Matrices)
 - Memory (M+, M-, MR, MC) & Timestamped History Tracker
 - Dual Interface: Interactive CLI & Modern Tkinter GUI
===============================================================================
"""

import sys
import math
import cmath
import ast
import operator
import datetime
import argparse
from typing import Any, Dict, List, Tuple, Union

# Optional Tkinter import for GUI mode
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


# =============================================================================
# 1. ANSI COLOR STYLING FOR CLI
# =============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

    @classmethod
    def disable(cls):
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.YELLOW = ''
        cls.RED = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''
        cls.RESET = ''


# Disable colors on non-tty terminals
if not sys.stdout.isatty():
    Colors.disable()


# =============================================================================
# 2. SAFE MATH EXPRESSION EVALUATOR (AST-BASED)
# =============================================================================
class MathEvaluator:
    """Evaluates mathematical expressions safely using Python's AST module."""

    def __init__(self):
        self.variables: Dict[str, float] = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'phi': (1 + math.sqrt(5)) / 2,
            'ans': 0.0,
            'm': 0.0
        }

        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
            ast.BitXor: operator.xor,
            ast.BitAnd: operator.and_,
            ast.BitOr: operator.or_,
            ast.Gt: operator.gt,
            ast.Lt: operator.lt,
            ast.GtE: operator.ge,
            ast.LtE: operator.le,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
        }

        self.functions = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'sqrt': math.sqrt,
            'cbrt': lambda x: math.pow(x, 1/3) if x >= 0 else -math.pow(-x, 1/3),
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'ln': math.log,
            'exp': math.exp,
            'abs': abs,
            'fact': math.factorial,
            'factorial': math.factorial,
            'floor': math.floor,
            'ceil': math.ceil,
            'deg': math.degrees,
            'rad': math.radians,
            'round': round,
        }

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        elif isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float, complex, bool)):
                return node.value
            raise ValueError(f"Invalid constant value: {node.value}")

        elif isinstance(node, ast.Num):  # Fallback for older AST
            return node.n

        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in self.variables:
                return self.variables[name]
            raise ValueError(f"Unknown variable or constant: '{node.id}'")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.operators:
                if op_type == ast.Div and right == 0:
                    raise ZeroDivisionError("Division by zero!")
                if op_type == ast.FloorDiv and right == 0:
                    raise ZeroDivisionError("Floor division by zero!")
                if op_type == ast.Mod and right == 0:
                    raise ZeroDivisionError("Modulo by zero!")
                return self.operators[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.operators:
                return self.operators[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comp in zip(node.ops, node.comparators):
                right = self._eval_node(comp)
                op_type = type(op)
                if op_type in self.operators:
                    if not self.operators[op_type](left, right):
                        return False
                    left = right
                else:
                    raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")
            return True

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported function call format")
            func_name = node.func.id.lower()
            if func_name not in self.functions:
                raise ValueError(f"Unknown function: '{node.func.id}'")
            
            args = [self._eval_node(arg) for arg in node.args]
            return self.functions[func_name](*args)

        else:
            raise ValueError(f"Unsupported syntax expression: {type(node).__name__}")

    def evaluate(self, expr_str: str) -> Union[int, float, complex]:
        """Parse and evaluate a math expression string."""
        if not expr_str or not expr_str.strip():
            raise ValueError("Expression is empty")

        # Clean string and convert '^' to '**' for exponentiation
        cleaned_expr = expr_str.strip().replace('^', '**')

        try:
            parsed = ast.parse(cleaned_expr, mode='eval')
            result = self._eval_node(parsed)
            # Update 'ans'
            if isinstance(result, (int, float)):
                self.variables['ans'] = float(result)
            return result
        except SyntaxError as se:
            raise ValueError(f"Invalid math syntax: {se.msg}")


# =============================================================================
# 3. CALCULATOR SPECIALIZED MODULES
# =============================================================================
class ScientificModule:
    """Scientific calculations: Trigonometry, Combinatorics, GCD/LCM, Primes."""

    @staticmethod
    def permutations(n: int, r: int) -> int:
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid parameters for nPr (must have n >= r >= 0)")
        return math.perm(n, r)

    @staticmethod
    def combinations(n: int, r: int) -> int:
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid parameters for nCr (must have n >= r >= 0)")
        return math.comb(n, r)

    @staticmethod
    def gcd(a: int, b: int) -> int:
        return math.gcd(a, b)

    @staticmethod
    def lcm(a: int, b: int) -> int:
        return math.lcm(a, b)

    @staticmethod
    def is_prime(n: int) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    @staticmethod
    def prime_factors(n: int) -> List[int]:
        if n <= 1:
            return []
        factors = []
        d = 2
        temp = n
        while d * d <= temp:
            while temp % d == 0:
                factors.append(d)
                temp //= d
            d += 1
        if temp > 1:
            factors.append(temp)
        return factors


class StatsModule:
    """Statistical Analysis module for lists of numerical data."""

    @staticmethod
    def mean(data: List[float]) -> float:
        if not data:
            raise ValueError("Data list is empty")
        return sum(data) / len(data)

    @staticmethod
    def median(data: List[float]) -> float:
        if not data:
            raise ValueError("Data list is empty")
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0
        return float(sorted_data[mid])

    @staticmethod
    def mode(data: List[float]) -> float:
        if not data:
            raise ValueError("Data list is empty")
        counts: Dict[float, int] = {}
        for val in data:
            counts[val] = counts.get(val, 0) + 1
        max_freq = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_freq]
        return modes[0]  # Return primary mode

    @staticmethod
    def variance(data: List[float], sample: bool = True) -> float:
        if len(data) < 2 and sample:
            raise ValueError("Sample variance requires at least 2 data points")
        if not data:
            raise ValueError("Data list is empty")
        m = StatsModule.mean(data)
        denom = (len(data) - 1) if sample else len(data)
        return sum((x - m) ** 2 for x in data) / denom

    @staticmethod
    def std_dev(data: List[float], sample: bool = True) -> float:
        return math.sqrt(StatsModule.variance(data, sample=sample))


class FinancialModule:
    """Financial tools: Interest and Loan EMI calculations."""

    @staticmethod
    def simple_interest(principal: float, rate: float, time_years: float) -> Tuple[float, float]:
        """Returns (Interest, Total Amount)"""
        interest = (principal * rate * time_years) / 100.0
        total = principal + interest
        return interest, total

    @staticmethod
    def compound_interest(principal: float, rate: float, time_years: float, n_compounds: int = 1) -> Tuple[float, float]:
        """Returns (Interest, Total Amount)"""
        r = rate / 100.0
        total = principal * math.pow(1 + (r / n_compounds), n_compounds * time_years)
        interest = total - principal
        return interest, total

    @staticmethod
    def loan_emi(principal: float, annual_rate: float, tenure_months: int) -> Tuple[float, float, float]:
        """Returns (Monthly EMI, Total Payment, Total Interest)"""
        if principal <= 0 or tenure_months <= 0:
            raise ValueError("Principal and tenure must be positive")
        
        monthly_rate = (annual_rate / 12.0) / 100.0
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / (math.pow(1 + monthly_rate, tenure_months) - 1)
        
        total_payment = emi * tenure_months
        total_interest = total_payment - principal
        return emi, total_payment, total_interest


class BaseBitwiseModule:
    """Base Conversion (Dec/Bin/Oct/Hex) and Bitwise operations."""

    @staticmethod
    def convert_base(num_str: str, from_base: int, to_base: int) -> str:
        value = int(num_str, from_base)
        if to_base == 10:
            return str(value)
        elif to_base == 2:
            return bin(value)
        elif to_base == 8:
            return oct(value)
        elif to_base == 16:
            return hex(value).upper()
        else:
            raise ValueError("Supported bases are 2, 8, 10, 16")

    @staticmethod
    def bitwise_op(a: int, b: int, op: str) -> int:
        if op == 'AND':
            return a & b
        elif op == 'OR':
            return a | b
        elif op == 'XOR':
            return a ^ b
        elif op == 'LSHIFT':
            return a << b
        elif op == 'RSHIFT':
            return a >> b
        else:
            raise ValueError(f"Unknown bitwise operator: {op}")


class UnitConverterModule:
    """Multi-Unit conversion tool."""

    LENGTH_FACTORS = {
        'meter': 1.0,
        'kilometer': 1000.0,
        'centimeter': 0.01,
        'millimeter': 0.001,
        'mile': 1609.344,
        'yard': 0.9144,
        'foot': 0.3048,
        'inch': 0.0254
    }

    MASS_FACTORS = {
        'kilogram': 1.0,
        'gram': 0.001,
        'milligram': 0.000001,
        'pound': 0.45359237,
        'ounce': 0.028349523125,
        'metric_ton': 1000.0
    }

    DATA_FACTORS = {
        'byte': 1.0,
        'kilobyte': 1024.0,
        'megabyte': 1024.0 ** 2,
        'gigabyte': 1024.0 ** 3,
        'terabyte': 1024.0 ** 4
    }

    @classmethod
    def convert_length(cls, val: float, from_u: str, to_u: str) -> float:
        if from_u not in cls.LENGTH_FACTORS or to_u not in cls.LENGTH_FACTORS:
            raise ValueError("Unsupported length unit")
        meters = val * cls.LENGTH_FACTORS[from_u]
        return meters / cls.LENGTH_FACTORS[to_u]

    @classmethod
    def convert_mass(cls, val: float, from_u: str, to_u: str) -> float:
        if from_u not in cls.MASS_FACTORS or to_u not in cls.MASS_FACTORS:
            raise ValueError("Unsupported mass unit")
        kg = val * cls.MASS_FACTORS[from_u]
        return kg / cls.MASS_FACTORS[to_u]

    @classmethod
    def convert_temperature(cls, val: float, from_u: str, to_u: str) -> float:
        # Convert to Celsius first
        if from_u == 'celsius':
            c = val
        elif from_u == 'fahrenheit':
            c = (val - 32.0) * 5.0 / 9.0
        elif from_u == 'kelvin':
            c = val - 273.15
        else:
            raise ValueError("Unsupported temperature unit")

        # Convert Celsius to target
        if to_u == 'celsius':
            return c
        elif to_u == 'fahrenheit':
            return (c * 9.0 / 5.0) + 32.0
        elif to_u == 'kelvin':
            return c + 273.15
        else:
            raise ValueError("Unsupported temperature unit")

    @classmethod
    def convert_data(cls, val: float, from_u: str, to_u: str) -> float:
        if from_u not in cls.DATA_FACTORS or to_u not in cls.DATA_FACTORS:
            raise ValueError("Unsupported data unit")
        bytes_val = val * cls.DATA_FACTORS[from_u]
        return bytes_val / cls.DATA_FACTORS[to_u]


class EquationAndMatrixModule:
    """Equation Solvers (Quadratic, Linear Systems) and Matrix algebra."""

    @staticmethod
    def solve_quadratic(a: float, b: float, c: float) -> Tuple[Union[float, complex], Union[float, complex], str]:
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero in a quadratic equation")
        disc = b**2 - 4*a*c
        if disc > 0:
            root1 = (-b + math.sqrt(disc)) / (2 * a)
            root2 = (-b - math.sqrt(disc)) / (2 * a)
            desc = "Two distinct real roots"
        elif disc == 0:
            root1 = root2 = -b / (2 * a)
            desc = "One repeated real root"
        else:
            root1 = (-b + cmath.sqrt(disc)) / (2 * a)
            root2 = (-b - cmath.sqrt(disc)) / (2 * a)
            desc = "Two complex conjugate roots"
        return root1, root2, desc

    @staticmethod
    def solve_linear_2x2(a1: float, b1: float, c1: float,
                         a2: float, b2: float, c2: float) -> Tuple[float, float]:
        """Solves system: a1*x + b1*y = c1 and a2*x + b2*y = c2 using Cramer's Rule."""
        det = a1 * b2 - a2 * b1
        if det == 0:
            raise ValueError("System has no unique solution (Determinant is 0)")
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        return x, y

    @staticmethod
    def matrix_2x2_det(m: List[List[float]]) -> float:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]

    @staticmethod
    def matrix_2x2_inv(m: List[List[float]]) -> List[List[float]]:
        det = EquationAndMatrixModule.matrix_2x2_det(m)
        if det == 0:
            raise ValueError("Matrix is singular (Determinant = 0), cannot invert")
        return [
            [m[1][1] / det, -m[0][1] / det],
            [-m[1][0] / det, m[0][0] / det]
        ]

    @staticmethod
    def matrix_mult(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        rows_A = len(A)
        cols_A = len(A[0])
        rows_B = len(B)
        cols_B = len(B[0])

        if cols_A != rows_B:
            raise ValueError(f"Cannot multiply matrix {rows_A}x{cols_A} with {rows_B}x{cols_B}")

        result = [[0.0 for _ in range(cols_B)] for _ in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    result[i][j] += A[i][k] * B[k][j]
        return result


# =============================================================================
# 4. HISTORY AND MEMORY MANAGER
# =============================================================================
class HistoryAndMemoryManager:
    """Manages memory registers and timestamped calculation logs."""

    def __init__(self):
        self.memory: float = 0.0
        self.history: List[Dict[str, str]] = []

    def add_history(self, expression: str, result: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history.append({
            'time': timestamp,
            'expr': expression,
            'result': result
        })

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def clear_history(self):
        self.history.clear()

    def m_add(self, val: float):
        self.memory += val

    def m_sub(self, val: float):
        self.memory -= val

    def m_recall(self) -> float:
        return self.memory

    def m_clear(self):
        self.memory = 0.0


# =============================================================================
# 5. INTERACTIVE CLI INTERFACE
# =============================================================================
class SuperCalculatorCLI:
    """Command Line Interface for Super Calculator."""

    def __init__(self):
        self.evaluator = MathEvaluator()
        self.history_mgr = HistoryAndMemoryManager()

    def print_banner(self):
        banner = f"""
{Colors.CYAN}{Colors.BOLD}===============================================================================
               ____  _   _ ____  _____ ____      ____    _    _     ____  
              / ___|| | | |  _ \| ____|  _ \    / ___|  / \  | |   / ___| 
              \___ \| | | | |_) |  _| | |_) |  | |     / _ \ | |  | |     
               ___) | |_| |  __/| |___|  _ <   | |___ / ___ \| |__| |___  
              |____/ \___/|_|   |_____|_| \_\   \____/_/   \_\_____\____| 
                                                                          
                          CSE 3206 - Student ID: 2203036
==============================================================================={Colors.RESET}
"""
        print(banner)

    def print_main_menu(self):
        print(f"\n{Colors.YELLOW}{Colors.BOLD}--- MAIN MENU ---{Colors.RESET}")
        print(f"{Colors.GREEN}[1]{Colors.RESET} Expression Evaluator (Standard / Scientific Math)")
        print(f"{Colors.GREEN}[2]{Colors.RESET} Scientific & Combinatorics Tools (nPr, nCr, GCD, LCM, Primes)")
        print(f"{Colors.GREEN}[3]{Colors.RESET} Statistical Analysis Module")
        print(f"{Colors.GREEN}[4]{Colors.RESET} Financial Tools (Interest & EMI)")
        print(f"{Colors.GREEN}[5]{Colors.RESET} Base & Bitwise Converter")
        print(f"{Colors.GREEN}[6]{Colors.RESET} Multi-Unit Converter")
        print(f"{Colors.GREEN}[7]{Colors.RESET} Equation Solver & Matrix Operations")
        print(f"{Colors.GREEN}[8]{Colors.RESET} Memory & History Log")
        if TKINTER_AVAILABLE:
            print(f"{Colors.GREEN}[9]{Colors.RESET} Launch Tkinter GUI Mode 🚀")
        print(f"{Colors.RED}[0]{Colors.RESET} Exit Application")

    def run_expression_evaluator(self):
        print(f"\n{Colors.CYAN}--- Direct Math Expression Evaluator ---{Colors.RESET}")
        print("Type math expression (e.g., '2 + 3 * sin(rad(45)) + sqrt(16)^2'). Type 'back' to return.")
        print("Variables available: pi, e, tau, phi, ans, m")
        while True:
            try:
                expr = input(f"{Colors.BOLD}Math> {Colors.RESET}").strip()
                if expr.lower() in ('back', 'exit', 'q'):
                    break
                if not expr:
                    continue

                res = self.evaluator.evaluate(expr)
                res_str = f"{res:.10g}" if isinstance(res, float) else str(res)
                print(f"{Colors.GREEN}= {res_str}{Colors.RESET}")
                self.history_mgr.add_history(expr, res_str)
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_scientific_tools(self):
        print(f"\n{Colors.CYAN}--- Scientific & Combinatorics Tools ---{Colors.RESET}")
        print("1. Permutations (nPr)")
        print("2. Combinations (nCr)")
        print("3. GCD & LCM")
        print("4. Prime Number Check & Factors")
        print("0. Back")

        choice = input("Select option: ").strip()
        try:
            if choice == '1':
                n = int(input("Enter n: "))
                r = int(input("Enter r: "))
                res = ScientificModule.permutations(n, r)
                print(f"{Colors.GREEN}nPr({n}, {r}) = {res}{Colors.RESET}")
            elif choice == '2':
                n = int(input("Enter n: "))
                r = int(input("Enter r: "))
                res = ScientificModule.combinations(n, r)
                print(f"{Colors.GREEN}nCr({n}, {r}) = {res}{Colors.RESET}")
            elif choice == '3':
                a = int(input("Enter integer a: "))
                b = int(input("Enter integer b: "))
                g = ScientificModule.gcd(a, b)
                l = ScientificModule.lcm(a, b)
                print(f"{Colors.GREEN}GCD({a}, {b}) = {g} | LCM({a}, {b}) = {l}{Colors.RESET}")
            elif choice == '4':
                n = int(input("Enter integer n: "))
                isp = ScientificModule.is_prime(n)
                factors = ScientificModule.prime_factors(n)
                print(f"{Colors.GREEN}Is Prime: {isp} | Prime Factors: {factors}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_statistics(self):
        print(f"\n{Colors.CYAN}--- Statistical Analysis ---{Colors.RESET}")
        try:
            raw = input("Enter numbers separated by spaces or commas: ").strip()
            if not raw:
                return
            nums = [float(x) for x in raw.replace(',', ' ').split()]
            print(f"\n{Colors.GREEN}Count:{Colors.RESET} {len(nums)}")
            print(f"{Colors.GREEN}Mean:{Colors.RESET} {StatsModule.mean(nums):.6g}")
            print(f"{Colors.GREEN}Median:{Colors.RESET} {StatsModule.median(nums):.6g}")
            print(f"{Colors.GREEN}Mode:{Colors.RESET} {StatsModule.mode(nums):.6g}")
            print(f"{Colors.GREEN}Min / Max:{Colors.RESET} {min(nums)} / {max(nums)}")
            print(f"{Colors.GREEN}Range:{Colors.RESET} {max(nums) - min(nums):.6g}")
            if len(nums) >= 2:
                print(f"{Colors.GREEN}Sample Std Dev:{Colors.RESET} {StatsModule.std_dev(nums, sample=True):.6g}")
                print(f"{Colors.GREEN}Sample Variance:{Colors.RESET} {StatsModule.variance(nums, sample=True):.6g}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_financial_tools(self):
        print(f"\n{Colors.CYAN}--- Financial Tools ---{Colors.RESET}")
        print("1. Simple Interest")
        print("2. Compound Interest")
        print("3. Loan EMI Calculator")
        choice = input("Select option: ").strip()
        try:
            if choice == '1':
                p = float(input("Principal Amount: "))
                r = float(input("Annual Interest Rate (%): "))
                t = float(input("Time Period (Years): "))
                interest, total = FinancialModule.simple_interest(p, r, t)
                print(f"{Colors.GREEN}Interest: {interest:.2f} | Total Amount: {total:.2f}{Colors.RESET}")
            elif choice == '2':
                p = float(input("Principal Amount: "))
                r = float(input("Annual Interest Rate (%): "))
                t = float(input("Time Period (Years): "))
                n = int(input("Compounds per year (1=annual, 12=monthly): "))
                interest, total = FinancialModule.compound_interest(p, r, t, n)
                print(f"{Colors.GREEN}Compound Interest: {interest:.2f} | Total Amount: {total:.2f}{Colors.RESET}")
            elif choice == '3':
                p = float(input("Loan Amount: "))
                r = float(input("Annual Interest Rate (%): "))
                m = int(input("Tenure (Months): "))
                emi, total_p, total_i = FinancialModule.loan_emi(p, r, m)
                print(f"{Colors.GREEN}Monthly EMI: {emi:.2f}")
                print(f"Total Interest: {total_i:.2f} | Total Repayment: {total_p:.2f}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_base_bitwise(self):
        print(f"\n{Colors.CYAN}--- Base & Bitwise Converter ---{Colors.RESET}")
        print("1. Base Converter (Dec/Bin/Oct/Hex)")
        print("2. Bitwise Operation (AND, OR, XOR, Shift)")
        choice = input("Select option: ").strip()
        try:
            if choice == '1':
                val = input("Enter number string: ").strip()
                from_b = int(input("From Base (2, 8, 10, 16): "))
                to_b = int(input("To Base (2, 8, 10, 16): "))
                res = BaseBitwiseModule.convert_base(val, from_b, to_b)
                print(f"{Colors.GREEN}Result: {res}{Colors.RESET}")
            elif choice == '2':
                a = int(input("First Integer: "))
                b = int(input("Second Integer: "))
                op = input("Operation (AND, OR, XOR, LSHIFT, RSHIFT): ").strip().upper()
                res = BaseBitwiseModule.bitwise_op(a, b, op)
                print(f"{Colors.GREEN}Result: {res} (Bin: {bin(res)}){Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_unit_converter(self):
        print(f"\n{Colors.CYAN}--- Multi-Unit Converter ---{Colors.RESET}")
        print("Categories: 1. Length  2. Mass  3. Temperature  4. Data Storage")
        cat = input("Select Category: ").strip()
        try:
            if cat == '1':
                print(f"Supported units: {list(UnitConverterModule.LENGTH_FACTORS.keys())}")
                val = float(input("Value: "))
                fu = input("From Unit: ").strip().lower()
                tu = input("To Unit: ").strip().lower()
                res = UnitConverterModule.convert_length(val, fu, tu)
                print(f"{Colors.GREEN}{val} {fu} = {res:.6g} {tu}{Colors.RESET}")
            elif cat == '2':
                print(f"Supported units: {list(UnitConverterModule.MASS_FACTORS.keys())}")
                val = float(input("Value: "))
                fu = input("From Unit: ").strip().lower()
                tu = input("To Unit: ").strip().lower()
                res = UnitConverterModule.convert_mass(val, fu, tu)
                print(f"{Colors.GREEN}{val} {fu} = {res:.6g} {tu}{Colors.RESET}")
            elif cat == '3':
                val = float(input("Value: "))
                fu = input("From Unit (celsius, fahrenheit, kelvin): ").strip().lower()
                tu = input("To Unit (celsius, fahrenheit, kelvin): ").strip().lower()
                res = UnitConverterModule.convert_temperature(val, fu, tu)
                print(f"{Colors.GREEN}{val} {fu} = {res:.4f} {tu}{Colors.RESET}")
            elif cat == '4':
                print(f"Supported units: {list(UnitConverterModule.DATA_FACTORS.keys())}")
                val = float(input("Value: "))
                fu = input("From Unit: ").strip().lower()
                tu = input("To Unit: ").strip().lower()
                res = UnitConverterModule.convert_data(val, fu, tu)
                print(f"{Colors.GREEN}{val} {fu} = {res:.6g} {tu}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run_solvers_and_matrices(self):
        print(f"\n{Colors.CYAN}--- Solvers & Matrix Algebra ---{Colors.RESET}")
        print("1. Solve Quadratic Equation (ax^2 + bx + c = 0)")
        print("2. Solve 2x2 Linear System (a1*x + b1*y = c1)")
        print("3. 2x2 Matrix Multiplication & Determinant")
        choice = input("Select option: ").strip()
        try:
            if choice == '1':
                a = float(input("Enter a: "))
                b = float(input("Enter b: "))
                c = float(input("Enter c: "))
                r1, r2, desc = EquationAndMatrixModule.solve_quadratic(a, b, c)
                print(f"{Colors.GREEN}Status: {desc}")
                print(f"Root 1: {r1}")
                print(f"Root 2: {r2}{Colors.RESET}")
            elif choice == '2':
                print("Eq 1: a1*x + b1*y = c1")
                a1 = float(input("a1: ")); b1 = float(input("b1: ")); c1 = float(input("c1: "))
                print("Eq 2: a2*x + b2*y = c2")
                a2 = float(input("a2: ")); b2 = float(input("b2: ")); c2 = float(input("c2: "))
                x, y = EquationAndMatrixModule.solve_linear_2x2(a1, b1, c1, a2, b2, c2)
                print(f"{Colors.GREEN}Solution: x = {x:.6g}, y = {y:.6g}{Colors.RESET}")
            elif choice == '3':
                print("Enter Matrix A (2x2):")
                a00 = float(input("A[0][0]: ")); a01 = float(input("A[0][1]: "))
                a10 = float(input("A[1][0]: ")); a11 = float(input("A[1][1]: "))
                mA = [[a00, a01], [a10, a11]]
                detA = EquationAndMatrixModule.matrix_2x2_det(mA)
                print(f"{Colors.GREEN}Determinant det(A) = {detA}{Colors.RESET}")
                inv_choice = input("Compute inverse of A? (y/n): ").strip().lower()
                if inv_choice == 'y':
                    invA = EquationAndMatrixModule.matrix_2x2_inv(mA)
                    print(f"{Colors.GREEN}Inverse A^-1:\n[{invA[0][0]:.4g}, {invA[0][1]:.4g}]\n[{invA[1][0]:.4g}, {invA[1][1]:.4g}]{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def show_memory_and_history(self):
        print(f"\n{Colors.CYAN}--- Memory & History Log ---{Colors.RESET}")
        print(f"Current Memory Register (M): {self.history_mgr.m_recall()}")
        print("\nCalculation History:")
        hist = self.history_mgr.get_history()
        if not hist:
            print("  [No history records yet]")
        else:
            for item in hist[-15:]:  # show last 15
                print(f"  [{item['time']}]  {item['expr']} = {item['result']}")

    def start(self):
        self.print_banner()
        while True:
            self.print_main_menu()
            choice = input(f"\n{Colors.BOLD}Select [0-9]: {Colors.RESET}").strip()
            if choice == '1':
                self.run_expression_evaluator()
            elif choice == '2':
                self.run_scientific_tools()
            elif choice == '3':
                self.run_statistics()
            elif choice == '4':
                self.run_financial_tools()
            elif choice == '5':
                self.run_base_bitwise()
            elif choice == '6':
                self.run_unit_converter()
            elif choice == '7':
                self.run_solvers_and_matrices()
            elif choice == '8':
                self.show_memory_and_history()
            elif choice == '9' and TKINTER_AVAILABLE:
                launch_gui()
            elif choice == '0':
                print(f"\n{Colors.CYAN}Thank you for using Super Calculator! Goodbye!{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid selection. Please enter a valid menu option.{Colors.RESET}")


# =============================================================================
# 6. TKINTER GRAPHICAL USER INTERFACE (GUI)
# =============================================================================
def launch_gui():
    if not TKINTER_AVAILABLE:
        print(f"{Colors.RED}Tkinter is not available in this Python environment.{Colors.RESET}")
        return

    root = tk.Tk()
    root.title("Super Calculator - Student ID 2203036")
    root.geometry("450x650")
    root.configure(bg="#1e1e2e")

    evaluator = MathEvaluator()
    history_mgr = HistoryAndMemoryManager()

    # Styling
    style = ttk.Style()
    style.theme_use('default')

    # Display entry
    display_var = tk.StringVar(value="")
    result_var = tk.StringVar(value="0")

    header_frame = tk.Frame(root, bg="#1e1e2e")
    header_frame.pack(fill="x", padx=15, pady=(15, 5))

    lbl_title = tk.Label(header_frame, text="SUPER CALCULATOR", font=("Helvetica", 14, "bold"), fg="#cba6f7", bg="#1e1e2e")
    lbl_title.pack(side="left")

    lbl_id = tk.Label(header_frame, text="ID: 2203036", font=("Helvetica", 10), fg="#a6adc8", bg="#1e1e2e")
    lbl_id.pack(side="right")

    # Display Frame
    disp_frame = tk.Frame(root, bg="#181825", bd=2, relief="sunken")
    disp_frame.pack(fill="x", padx=15, pady=10)

    entry_expr = tk.Entry(disp_frame, textvariable=display_var, font=("Consolas", 14), fg="#a6adc8", bg="#181825", bd=0, justify="right")
    entry_expr.pack(fill="x", padx=10, pady=(10, 2))

    lbl_result = tk.Label(disp_frame, textvariable=result_var, font=("Consolas", 22, "bold"), fg="#a6e3a1", bg="#181825", anchor="e")
    lbl_result.pack(fill="x", padx=10, pady=(0, 10))

    # Helper button callbacks
    def on_btn_click(char):
        display_var.set(display_var.get() + str(char))

    def on_clear():
        display_var.set("")
        result_var.set("0")

    def on_backspace():
        display_var.set(display_var.get()[:-1])

    def on_equal():
        expr = display_var.get()
        if not expr:
            return
        try:
            res = evaluator.evaluate(expr)
            res_str = f"{res:.10g}" if isinstance(res, float) else str(res)
            result_var.set(res_str)
            history_mgr.add_history(expr, res_str)
        except Exception as err:
            result_var.set("Error")
            messagebox.showerror("Math Error", str(err))

    # Keypad Grid
    grid_frame = tk.Frame(root, bg="#1e1e2e")
    grid_frame.pack(fill="both", expand=True, padx=15, pady=10)

    buttons = [
        ('MC', 'MR', 'M+', 'M-'),
        ('sin', 'cos', 'tan', 'sqrt'),
        ('log', 'ln', '^', '('),
        (')', 'C', '⌫', '/'),
        ('7', '8', '9', '*'),
        ('4', '5', '6', '-'),
        ('1', '2', '3', '+'),
        ('0', '.', 'pi', '=')
    ]

    for row_idx, row in enumerate(buttons):
        grid_frame.rowconfigure(row_idx, weight=1)
        for col_idx, btn_text in enumerate(row):
            grid_frame.columnconfigure(col_idx, weight=1)

            bg_color = "#313244"
            fg_color = "#cdd6f4"

            if btn_text in ('/', '*', '-', '+', '='):
                bg_color = "#fab387"
                fg_color = "#11111b"
            elif btn_text in ('C', '⌫'):
                bg_color = "#f38ba8"
                fg_color = "#11111b"
            elif btn_text in ('sin', 'cos', 'tan', 'sqrt', 'log', 'ln', '^', '(', ')', 'pi', 'MC', 'MR', 'M+', 'M-'):
                bg_color = "#45475a"
                fg_color = "#89b4fa"

            cmd = None
            if btn_text == 'C':
                cmd = on_clear
            elif btn_text == '⌫':
                cmd = on_backspace
            elif btn_text == '=':
                cmd = on_equal
            elif btn_text == 'MC':
                cmd = history_mgr.m_clear
            elif btn_text == 'MR':
                cmd = lambda: display_var.set(display_var.get() + str(history_mgr.m_recall()))
            elif btn_text == 'M+':
                cmd = lambda: history_mgr.m_add(float(result_var.get()) if result_var.get() != "Error" else 0)
            elif btn_text == 'M-':
                cmd = lambda: history_mgr.m_sub(float(result_var.get()) if result_var.get() != "Error" else 0)
            elif btn_text in ('sin', 'cos', 'tan', 'sqrt', 'log', 'ln'):
                cmd = lambda t=btn_text: on_btn_click(f"{t}(")
            else:
                cmd = lambda t=btn_text: on_btn_click(t)

            btn = tk.Button(
                grid_frame,
                text=btn_text,
                font=("Helvetica", 12, "bold"),
                bg=bg_color,
                fg=fg_color,
                bd=0,
                activebackground="#585b70",
                command=cmd
            )
            btn.grid(row=row_idx, column=col_idx, sticky="nsew", padx=3, pady=3)

    root.mainloop()


# =============================================================================
# 7. AUTOMATED SELF-TEST RUNNER
# =============================================================================
def run_self_tests():
    print(f"{Colors.CYAN}Running Super Calculator Self-Tests...{Colors.RESET}")
    evaluator = MathEvaluator()

    tests = [
        ("2 + 3 * 4", 14),
        ("sin(0)", 0),
        ("cos(0)", 1),
        ("sqrt(16) + cbrt(27)", 7),
        ("log10(100)", 2),
        ("fact(5)", 120),
        ("2^3", 8),
        ("pi > 3", True),
    ]

    passed = 0
    for expr, expected in tests:
        res = evaluator.evaluate(expr)
        if math.isclose(res, expected, rel_tol=1e-5) if isinstance(expected, (int, float)) else res == expected:
            passed += 1
            print(f"  {Colors.GREEN}✓ PASSED:{Colors.RESET} '{expr}' = {res}")
        else:
            print(f"  {Colors.RED}✗ FAILED:{Colors.RESET} '{expr}' expected {expected}, got {res}")

    print(f"\n{Colors.GREEN}Self-Test Summary: {passed}/{len(tests)} tests passed!{Colors.RESET}\n")


# =============================================================================
# 8. MAIN ENTRYPOINT
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Super Calculator - CSE 3206 (ID: 2203036)")
    parser.add_argument("expression", nargs="?", help="Direct mathematical expression to evaluate")
    parser.add_argument("--cli", action="store_true", help="Launch interactive CLI mode directly")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI mode directly")
    parser.add_argument("--test", action="store_true", help="Run internal self-tests")

    args = parser.parse_args()

    if args.test:
        run_self_tests()
        return

    if args.expression:
        evaluator = MathEvaluator()
        try:
            res = evaluator.evaluate(args.expression)
            print(f"{res}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.gui:
        launch_gui()
        return

    if args.cli:
        cli = SuperCalculatorCLI()
        cli.start()
        return

    # If launched without arguments, check CLI vs GUI selection
    if TKINTER_AVAILABLE and sys.stdout.isatty():
        cli = SuperCalculatorCLI()
        cli.start()
    else:
        cli = SuperCalculatorCLI()
        cli.start()


if __name__ == '__main__':
    main()
