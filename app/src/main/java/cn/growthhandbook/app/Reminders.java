package cn.growthhandbook.app;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import org.json.JSONArray;
import org.json.JSONObject;

/** Vaccine and check-up reminders computed by the page from the birth date, kept here so they survive reboots. */
final class Reminders {
    static final String PREFS = "reminders", KEY = "events", COUNT = "count", CHANNEL = "care", JKEY = "journal", JCOUNT = "jcount", JCHANNEL = "journal";

    static void save(Context c, String json) {
        c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString(KEY, json == null ? "[]" : json).apply();
    }

    // 育儿手帐 reminders (vitamin D, time since the last feed), set from the journal page and kept apart from the care list
    static void saveJournal(Context c, String json) {
        c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString(JKEY, json == null ? "[]" : json).apply();
    }

    static void schedule(Context c) {
        scheduleCare(c);
        SharedPreferences p = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        int old = p.getInt(JCOUNT, 0);
        for (int i = 0; i < old; i++) am.cancel(pendingJ(c, i, null, null));
        int n = 0;
        try {
            JSONArray ev = new JSONArray(p.getString(JKEY, "[]"));
            long now = System.currentTimeMillis();
            for (int i = 0; i < ev.length() && n < 60; i++) {
                JSONObject e = ev.getJSONObject(i);
                long t = e.getLong("t");
                if (t <= now) continue;
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pendingJ(c, n, e.optString("title"), e.optString("text")));
                n++;
            }
        } catch (Exception ignored) { }
        p.edit().putInt(JCOUNT, n).apply();
    }

    static PendingIntent pendingJ(Context c, int id, String title, String text) {
        Intent i = new Intent(c, ReminderReceiver.class);
        if (title != null) { i.putExtra("title", title); i.putExtra("text", text); i.putExtra("page", "journal"); }
        return PendingIntent.getBroadcast(c, 5000 + id, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static void scheduleCare(Context c) {
        SharedPreferences p = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        int old = p.getInt(COUNT, 0);
        for (int i = 0; i < old; i++) am.cancel(pending(c, i, null, null, -1));
        int n = 0;
        try {
            JSONArray ev = new JSONArray(p.getString(KEY, "[]"));
            long now = System.currentTimeMillis();
            for (int i = 0; i < ev.length(); i++) {
                JSONObject e = ev.getJSONObject(i);
                long t = e.getLong("t");
                if (t <= now) continue;
                PendingIntent pi = pending(c, n, e.optString("title"), e.optString("text"), e.optInt("m", -1));
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi);
                n++;
            }
        } catch (Exception ignored) { }
        p.edit().putInt(COUNT, n).apply();
    }

    static PendingIntent pending(Context c, int id, String title, String text, int month) {
        Intent i = new Intent(c, ReminderReceiver.class);
        if (title != null) { i.putExtra("title", title); i.putExtra("text", text); i.putExtra("month", month); }
        return PendingIntent.getBroadcast(c, 1000 + id, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    static void channel(Context c) {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            NotificationChannel ch = new NotificationChannel(CHANNEL, c.getString(R.string.channel_name), NotificationManager.IMPORTANCE_DEFAULT);
            nm.createNotificationChannel(ch);
            nm.createNotificationChannel(new NotificationChannel(JCHANNEL, "手帐提醒", NotificationManager.IMPORTANCE_DEFAULT));
        }
    }

    private Reminders() { }
}
