from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import itertools

# Initialize FastAPI app
app = FastAPI()

# Set up templates and static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


def calculate_destiny_number(birthdate: str) -> int:
    """
    Calculate the Destiny Number (Life Path Number) from a given birthdate.
    
    Args:
    - birthdate (str): Birthdate in the format 'YYYY-MM-DD'
    
    Returns:
    - int: The Destiny (Life Path) number
    """
    # Split the birthdate into year, month, and day
    year, month, day = map(int, birthdate.split('-'))
    
    # Reduce the components to a single digit (or Master Number)
    def reduce_to_single_digit(number):
        while number > 9 and number not in [11, 22, 33]:  # Master Numbers
            number = sum(int(digit) for digit in str(number))
        return number
    
    # Calculate life path by summing year, month, and day
    year_sum = reduce_to_single_digit(year)
    month_sum = reduce_to_single_digit(month)
    day_sum = reduce_to_single_digit(day)
    
    # Add the sums and reduce again to a single digit
    total_sum = year_sum + month_sum + day_sum
    return reduce_to_single_digit(total_sum)


def calculate_root_number(birthdate: str) -> int:
    """
    Calculate the Root Number from the given birthdate's day (DD).
    
    Args:
    - birthdate (str): Birthdate in the format 'YYYY-MM-DD'
    
    Returns:
    - int: The Root Number (based on the day of birth)
    """
    # Extract the day (DD) from the birthdate
    day = int(birthdate.split('-')[2])
    
    # Sum the digits of the day
    total_sum = sum(int(digit) for digit in str(day))
    
    # Reduce the sum to a single digit (or Master Number)
    def reduce_to_single_digit(number):
        while number > 9 and number not in [11, 22, 33]:  # Master Numbers
            number = sum(int(digit) for digit in str(number))
        return number
    
    return reduce_to_single_digit(total_sum)


# Chaldean Numerology Calculation
def calculate_chaldean_number(name: str) -> int:
    chaldean_chart = {
        "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
        "B": 2, "K": 2, "R": 2,
        "C": 3, "G": 3, "L": 3, "S": 3,
        "D": 4, "M": 4, "T": 4,
        "E": 5, "H": 5, "N": 5, "X": 5,
        "U": 6, "V": 6, "W": 6,
        "O": 7, "Z": 7,
        "F": 8, "P": 8
    }
    name = name.upper().replace(" ", "")
    name_sum = sum(chaldean_chart.get(char, 0) for char in name if char in chaldean_chart)
    while name_sum > 9 and name_sum not in {11, 22}:
        name_sum = sum(int(digit) for digit in str(name_sum))
    return name_sum

# Predefined 3x3 grid layout
VEDIC_MATRIX = [
    [3, 1, 9],
    [6, 7, 5],
    [2, 8, 4]
]



def generate_vedic_grid_dynamic(birthdate: str):
    """
    Generate a 3x3 Vedic numerology grid where numbers appear based on their frequency in the DOB.
    """
    # Flatten the predefined grid to validate positions
    flat_matrix = list(itertools.chain(*VEDIC_MATRIX))

    # Count occurrences of each number in the DOB
    dob_digits = [int(digit) for digit in birthdate if digit.isdigit()]
    dob_digits.append(calculate_destiny_number(birthdate))  # Add Destiny Number
    dob_digits.append(calculate_root_number(birthdate))  # Add Root Number
    # remove first 2 digits
    dob_digits = dob_digits[2:]
    frequency = {num: dob_digits.count(num) for num in range(1, 10)}

    # Generate the grid with counts
    grid = []
    for row in VEDIC_MATRIX:
        grid_row = []
        for num in row:
            grid_row.append(str(num) * frequency[num])  # Repeat the number based on its frequency
        grid.append(grid_row)

    return grid

def find_missing_numbers_dynamic(birthdate: str):
    """
    Identify numbers missing in the DOB.
    """
    dob_digits = set(int(digit) for digit in birthdate if digit.isdigit())
    all_numbers = set(range(1, 10))
    return sorted(all_numbers - dob_digits)

# Root route for form submission
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/result", response_class=HTMLResponse)
async def post_result(request: Request, name: str = Form(...), birthdate: str = Form(...)):
    chaldean_number = calculate_chaldean_number(name)
    vedic_grid = generate_vedic_grid_dynamic(birthdate)
    missing_numbers = find_missing_numbers_dynamic(birthdate)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": {
                "name": name,
                "birthdate": birthdate,
                "chaldean_number": chaldean_number,
                "vedic_grid": vedic_grid,
                "grid_layout": VEDIC_MATRIX,  # Original matrix for subscripts
                "missing_numbers": missing_numbers,
            },
        },
    )

