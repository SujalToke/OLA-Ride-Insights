CREATE DATABASE OLA_RIDE_INSIGHTS;
USE OLA_RIDE_INSIGHTS;



select * from cleaned_ola_data;
describe cleaned_ola_data;


-- Q1. Retrieve all successful bookings

SELECT count(*)
FROM cleaned_ola_data
WHERE Booking_Status = 'Success';

-- Q2. Find the average ride distance for each vehicle type

SELECT
    Vehicle_Type,
    AVG(Ride_Distance) AS Average_Ride_Distance
FROM cleaned_ola_data
GROUP BY Vehicle_Type;

-- Q3. Get the total number of rides cancelled by customers

SELECT COUNT(*) AS Total_Customer_Cancellations
FROM cleaned_ola_data
WHERE Booking_Status = 'Canceled by Customer';

-- Q4. List the top 5 customers who booked the highest number of rides

SELECT
    Customer_ID,
    COUNT(Booking_ID) AS Total_Rides
FROM cleaned_ola_data
GROUP BY Customer_ID
ORDER BY Total_Rides DESC
LIMIT 5;

-- Q5. Get the number of rides cancelled by drivers due to personal and car-related issues

SELECT COUNT(*) AS Total_Driver_Cancellations
FROM cleaned_ola_data
WHERE Canceled_Rides_by_Driver =
      'Personal & Car related issue';
      
-- Q6. Find the maximum and minimum driver ratings for Prime Sedan bookings

SELECT
    MAX(Driver_Ratings) AS Maximum_Driver_Rating,
    MIN(Driver_Ratings) AS Minimum_Driver_Rating
FROM cleaned_ola_data
WHERE Vehicle_Type = 'Prime Sedan';

-- Q7. Retrieve all rides where payment was made using UPI

SELECT *
FROM cleaned_ola_data
WHERE Payment_Method = 'UPI';

-- Q8. Find the average customer rating per vehicle type

SELECT
    Vehicle_Type,
    AVG(Customer_Rating) AS Average_Customer_Rating
FROM cleaned_ola_data
GROUP BY Vehicle_Type;


-- Q9. Calculate the total booking value of successfully completed rides

SELECT
    SUM(Booking_Value) AS Total_Successful_Booking_Value
FROM cleaned_ola_data
WHERE Booking_Status = 'Success';

-- Q10. List all incomplete rides along with the reason

SELECT
    Booking_ID,
    Customer_ID,
    Incomplete_Rides,
    Incomplete_Rides_Reason
FROM cleaned_ola_data
WHERE Incomplete_Rides = 'Yes';
