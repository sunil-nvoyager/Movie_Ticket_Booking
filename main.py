import json
from typing import Optional

from fastapi.responses import JSONResponse
from objects.models import *
from controllers.ticketController import *
from fastapi import FastAPI
from datetime import datetime
from typing import List, Optional

app = FastAPI(
    title="Ticketly",
    description="A Movie Theatre Ticket booking System  "
)

ticketAdmin = TicketAdmin()


@app.post("/bookTicket",
summary = "Book Tickets",
description = "Book Tickets using a user's name ,phoneNumber, Timing, MovieName",
tags=["TicketBooking"]
) 
def bookTicket(userName: str, userPhoneNumber: str, movieName: str, movieStartTime: datetime, numTickets: int):
    user = ticketAdmin.resolveOrCreateUser(userName, userPhoneNumber)
    return ticketAdmin.bookCustomerTicket(user.userId, movieName, movieStartTime, numTickets)

@app.post("/updateMovieSlotForTicket",
summary = "Update a Ticket Time",
description = "Update Ticket Time by ticketId, newMovie and newStartTime",
tags=["Update Ticket Timing"])
def updateMovieSlotForTicket(ticketId: str, newMovie: str, newStartTime: datetime):
    ticket = ticketAdmin.getTicketById(ticketId)
    ticketSlot = ticketAdmin.resolveTicketSlot(newMovie, newStartTime)[0]
    return ticketAdmin.updateTicket(ticket, ticketSlot)
     

@app.post("/getAllTicketsForMovieSlot",
summary = "Get all Booked Tickets for a Movie Slot",
description = "Get Details Of all the tickets for a Movie Slot",
tags=["Ticket Details"])
def getAllTicketsForMovieSlot(movieName: str, movieStartTime: datetime):
    ticketSlots = ticketAdmin.resolveTicketSlot(movieName, movieStartTime)
    for ticketSlot in ticketSlots:
        return ticketAdmin.getBookedTickets(ticketSlot)
    return []
     
@app.post("/getUserDetailsByTicketId",
summary = "User Details",
description = "Get User Details By ticketId",
tags=["User Details"])
def getUserDetailsByTicketId(ticketId: str):
    ticket = ticketAdmin.getTicketById(ticketId)
    print(ticket, ticket.userId)
    user = ticketAdmin.getUserById(ticket.userId)
    return User.from_orm(user) 

@app.post("/cancelTicket",
summary = "Cancel Tickets",
description = "Cancel a Ticket By ticketId",
tags=[" Cancel Tickets"])
def cancelTicket(ticketId: str):
    ticket = ticketAdmin.getTicketById(ticketId)
    ticketSlot = ticketAdmin.getTicketSlotById(ticket.ticketSlotId)
    return ticketAdmin.cancelTicket(ticket, ticketSlot)


@app.post("/expireTickets",
summary = "Make Tickets Expire",
description = "Mark a ticket as expired if there is a diff of 8 hours between the ticket timing and current time",
tags=["Automated Ticket Expiry"])
def expiretickets():
    return ticketAdmin.invalidateTickets()

@app.post("/scheduleMovie",
summary = "Movie Scheduler",
description = "Add a movie to schedule",
tags=["Movie Scheduler"])
def scheduleMovie(slotName: str, slotDescription: str, \
                            startTime: datetime, \
                            endTime: datetime, \
                            slotType: SlotType, \
                            genre: Genre):
    return ticketAdmin.scheduleTicketSlot(slotName, slotDescription, startTime, endTime, slotType, genre)

@app.post("/getAllMovieSlots",
summary = "Movie Slots",
description = "Gives Details of all the movie slots",
tags=["Movie Slot Details"])
def getAllMovieSlotsByGenre():
    return ticketAdmin.getAllTicketSlots()



@app.post("/getAllMovieSlotsByGenre",
summary = "Movie Slots Genre",
description = "Gives Details of all the movie slots by Genre",
tags=["Movie Slot Details"])
def getAllMovieSlotsByGenre(genre: Genre):
    return ticketAdmin.getAllTicketSlotsByGenre(genre)


"""
#TODO: Desirable Non-Functional Requirement
@app.post("/getAllMovieSlotsAfterTime")
def getAllMovieSlotsAfterTime(inputTime: datetime):
    return ticketAdmin.getAllMovieSlotsAfterTime(inputTime)

@app.post("/getAllMovieSlotsBeforeTime")
def getAllMovieSlotsBeforeTime(inputTime: datetime):
    return ticketAdmin.getAllMovieSlotsAfterTime(inputTime)
"""

class RequestModel(BaseModel):
    id: str
    name: str
    version: Optional[str] = None  # Optional field with default value


# Define Response Model
class ResponseModel(BaseModel):
    success: bool
    message: str
    processed_name: str


# Create a POST endpoint to take request object and return response object
@app.post("/process", response_model=ResponseModel)
async def process_data(request: RequestModel):
    # Process the input data (this is where your logic goes)
    processed_name = request.name.upper()  # Example processing: make the name uppercase

    # Return the response object
    return ResponseModel(
        success=True,
        message="Data processed successfully",
        processed_name=processed_name
    )



# Path to your OpenAPI spec JSON file
OPENAPI_SPEC_PATH = "docs/openapi_penify.json"

@app.on_event("startup")
async def load_custom_openapi():
    if os.path.exists(OPENAPI_SPEC_PATH):
        with open(OPENAPI_SPEC_PATH, "r") as f:
            custom_openapi = json.load(f)
        app.openapi_schema = custom_openapi  # Override FastAPI's default OpenAPI schema
    else:
        print("Custom OpenAPI spec file not found. Using default schema.")


