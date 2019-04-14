import pendulum

def layout(today, start_date, end_date):
  calendar = []
  month = {}
  cur_month_number = -1
  for day in pendulum.period(start_date.start_of('month'), end_date.end_of('month')):
    if cur_month_number != day.month:
      if cur_month_number != -1:
        calendar.append(month)
      cur_month_number = day.month
      month = {'name': day.format('MMMM YYYY'), 'days': []}
    week_number = (day - start_date).in_days() // 7
    month['days'].append({
      'number': day.day,
      'of_week': day.day_of_week,
      'week_number': week_number,
      'is_today': today.date() == day.date()
    })
  calendar.append(month)
  return calendar
