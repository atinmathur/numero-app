from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os
import itertools
import json

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
    
    day = int(birthdate.split('-')[2])
    if day > 9 and day not in [10, 20, 30]:
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

def calculate_mahadasha_antardasha(birthdate: str, num_years: int = 90):
    birthdate_dt = datetime.strptime(birthdate, "%Y-%m-%d")
    day, month, year = birthdate_dt.day, birthdate_dt.month, birthdate_dt.year
    root_number = sum(int(digit) for digit in str(day))
    while root_number > 9:
        root_number = sum(int(digit) for digit in str(root_number))

    mahadasha_order = []
    start = root_number
    for _ in range(9):  # One cycle
        mahadasha_order.append(start)
        start += 1
        if start > 9:
            start = 1

    results = []
    current_year = year
    mahadasha_index = 0
    mahadasha_start_year = year

    for i in range(num_years):
        current_birthday = datetime(current_year + i, month, day)
        if current_year + i >= mahadasha_start_year + mahadasha_order[mahadasha_index]:
            mahadasha_index = (mahadasha_index + 1) % len(mahadasha_order)
            mahadasha_start_year = current_year + i

        mahadasha = mahadasha_order[mahadasha_index]
        sum_dob = day + month + (current_year + i) % 100
        weekday = current_birthday.weekday()
        weekday_map = {0: 2, 1: 9, 2: 5, 3: 3, 4: 6, 5: 8, 6: 1}
        sum_dob += weekday_map[weekday]
        while sum_dob > 9:
            sum_dob = sum(int(digit) for digit in str(sum_dob))
        antardasha = sum_dob
        running_age = (current_year + i) - year + 1
        results.append({
            "year": current_year + i,
            "start_date": current_birthday.strftime("%d-%m-%Y"),
            "running_age": running_age,
            "mahadasha": mahadasha,
            "antardasha": antardasha,
        })

    return results


# Root route for form submission
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/result", response_class=HTMLResponse)
async def post_result(request: Request, name: str = Form(...), birthdate: str = Form(...)):
    chaldean_number = calculate_chaldean_number(name)
    vedic_grid = generate_vedic_grid_dynamic(birthdate)
    mahadasha_periods = calculate_mahadasha_antardasha(birthdate)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "results": {
                "name": name,
                "birthdate": datetime.strptime(birthdate, "%Y-%m-%d").strftime("%d-%m-%Y"),
                "chaldean_number": chaldean_number,
                "vedic_grid": vedic_grid,
                "grid_layout": VEDIC_MATRIX,  # Original matrix for subscripts
                "mahadasha_periods": mahadasha_periods,
            },
        },
    )

# Function to update the grid based on Mahadasha and Antardasha
def update_vedic_grid(base_grid, mahadasha, antardasha):
    # Create a new updated grid
    updated_grid = []

    for row_index, row in enumerate(VEDIC_MATRIX):  # Iterate through the original Vedic matrix
        updated_row = []
        for col_index, cell in enumerate(row):
            # Get the current cell value from the base grid
            current_value = base_grid[row_index][col_index]

            # Append Mahadasha or Antardasha if the position matches
            if cell == mahadasha:
                current_value += str(mahadasha)
            if cell == antardasha:
                current_value += str(antardasha)

            updated_row.append(current_value)
        updated_grid.append(updated_row)

    return updated_grid

# Add endpoint for dynamically updating grid based on Mahadasha and Antardasha
@app.get("/update-grid")
async def update_grid(
    mahadasha: int, 
    antardasha: int, 
    base_grid: str
):
    # Convert the base grid from JSON string to Python list
    base_grid = json.loads(base_grid)
    print(base_grid)
    
    # Define your updated grid logic here
    updated_grid = update_vedic_grid(base_grid, mahadasha, antardasha)
    
    # Return updated grid as JSON response
    return JSONResponse(content={"updated_grid": updated_grid})
