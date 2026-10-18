package cn.growthhandbook.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Calendar;

/** Home-screen card: how old the baby is today and the next vaccine or check-up. */
public class AgeWidget extends AppWidgetProvider {
    static final String PREFS = "profile", BIRTH = "birth", NAME = "name";

    static void saveBirth(Context c, String birth) {
        c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString(BIRTH, birth == null ? "" : birth).apply();
        refresh(c);
    }

    static void saveName(Context c, String name) {
        c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString(NAME, name == null ? "" : name).apply();
        refresh(c);
    }

    static void refresh(Context c) {
        AppWidgetManager m = AppWidgetManager.getInstance(c);
        int[] ids = m.getAppWidgetIds(new ComponentName(c, AgeWidget.class));
        if (ids != null && ids.length > 0) new AgeWidget().onUpdate(c, m, ids);
    }

    // the same rule as the handbook: the same day of the month, or the last day of a shorter month
    static Calendar addMonths(Calendar b, int months) {
        Calendar x = (Calendar) b.clone();
        x.set(Calendar.DAY_OF_MONTH, 1);
        x.add(Calendar.MONTH, months);
        x.set(Calendar.DAY_OF_MONTH, Math.min(b.get(Calendar.DAY_OF_MONTH), x.getActualMaximum(Calendar.DAY_OF_MONTH)));
        return x;
    }

    static long days(Calendar a, Calendar b) { return Math.round((b.getTimeInMillis() - a.getTimeInMillis()) / 86400000.0); }

    @Override
    public void onUpdate(Context c, AppWidgetManager mgr, int[] ids) {
        String line1, line2;
        String birth = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(BIRTH, "");
        String name = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(NAME, "");
        if (name == null || name.trim().isEmpty()) name = "小怪兽";
        Calendar today = Calendar.getInstance();
        today.set(Calendar.HOUR_OF_DAY, 0); today.set(Calendar.MINUTE, 0); today.set(Calendar.SECOND, 0); today.set(Calendar.MILLISECOND, 0);
        if (birth == null || birth.isEmpty()) {
            line1 = "养小怪兽";
            line2 = "打开应用，填写" + name + "的出生日期";
        } else {
            String[] p = birth.split("-");
            Calendar b = Calendar.getInstance();
            b.clear(); b.set(Integer.parseInt(p[0]), Integer.parseInt(p[1]) - 1, Integer.parseInt(p[2]));
            int mo = (today.get(Calendar.YEAR) - b.get(Calendar.YEAR)) * 12 + today.get(Calendar.MONTH) - b.get(Calendar.MONTH);
            if (addMonths(b, mo).after(today)) mo--;
            if (mo < 0) { line1 = "养小怪兽"; line2 = "出生日期晚于今天"; }
            else {
                long d = days(addMonths(b, mo), today);
                line1 = name + "今天满 " + mo + " 个月" + (d > 0 ? " " + d + " 天" : "");
                line2 = nextCare(c, today);
            }
        }
        for (int id : ids) {
            RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.widget_age);
            v.setTextViewText(R.id.w_age, line1);
            v.setTextViewText(R.id.w_next, line2);
            Intent i = new Intent(c, MainActivity.class).setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            v.setOnClickPendingIntent(R.id.w_root, PendingIntent.getActivity(c, 7, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE));
            mgr.updateAppWidget(id, v);
        }
    }

    // the next day-of reminder the handbook set: "今天满 N 个月：接种和儿保"
    static String nextCare(Context c, Calendar today) {
        try {
            JSONArray ev = new JSONArray(c.getSharedPreferences(Reminders.PREFS, Context.MODE_PRIVATE).getString(Reminders.KEY, "[]"));
            JSONObject best = null;
            for (int i = 0; i < ev.length(); i++) {
                JSONObject e = ev.getJSONObject(i);
                if (!e.optString("title").startsWith("今天满")) continue;
                if (e.getLong("t") < today.getTimeInMillis()) continue;
                if (best == null || e.getLong("t") < best.getLong("t")) best = e;
            }
            if (best == null) return "接种和儿保日期都已过";
            Calendar t = Calendar.getInstance(); t.setTimeInMillis(best.getLong("t"));
            t.set(Calendar.HOUR_OF_DAY, 0); t.set(Calendar.MINUTE, 0); t.set(Calendar.SECOND, 0); t.set(Calendar.MILLISECOND, 0);
            long d = days(today, t);
            String title = best.optString("title"), what = title.contains("：") ? title.substring(title.indexOf("：") + 1) : "接种和儿保";
            return "满 " + best.optInt("m") + " 个月" + what + (d == 0 ? " · 今天" : " · " + d + " 天后");
        } catch (Exception e) { return ""; }
    }
}
