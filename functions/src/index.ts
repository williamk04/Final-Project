import { updateExpiredReservations } from "./functions/check_expired";
import { onSchedule } from "firebase-functions/scheduler";

export const cronUpdateExpired = onSchedule("every 5 minutes", async (event) => {
  console.log("Running scheduled task: update expired reservations");
  await updateExpiredReservations();
});
