package cn.growthhandbook.app;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

/** Shows one reminder; tapping it opens that month's vaccine and check-up section. */
public class ReminderReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent in) {
        String title = in.getStringExtra("title"), text = in.getStringExtra("text");
        int month = in.getIntExtra("month", -1);
        if (title == null) return;
        Reminders.channel(c);
        boolean jr = "journal".equals(in.getStringExtra("page"));
        Intent open = new Intent(c, MainActivity.class).putExtra("month", month).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        if (jr) open.putExtra("page", "journal");
        PendingIntent pi = PendingIntent.getActivity(c, jr ? 2900 : 2000 + Math.max(month, 0), open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, jr ? Reminders.JCHANNEL : Reminders.CHANNEL) : new Notification.Builder(c);
        b.setSmallIcon(R.drawable.ic_stat).setContentTitle(title).setContentText(text)
                .setStyle(new Notification.BigTextStyle().bigText(text)).setContentIntent(pi).setAutoCancel(true);
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        try { nm.notify(jr ? 3900 + (title.contains("维生素") ? 0 : 1) : 3000 + Math.max(month, 0) * 2 + (title.startsWith("3") ? 0 : 1), b.build()); } catch (SecurityException ignored) { }
    }
}
