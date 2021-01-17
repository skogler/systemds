@groovy.lang.GrabConfig(systemClassLoader = true)
@Grab(group = "org.apache.commons", module = "commons-email", version = "1.5")
@Grab(group = "com.opencsv", module = "opencsv", version = "5.3")
import org.apache.commons.mail.util.*
import com.opencsv.CSVWriter
import javax.activation.DataSource;
import javax.mail.Session;
import javax.mail.internet.MimeMessage;

CSVWriter writer = new CSVWriter(new FileWriter("yourfile.csv"));

dia = new File("/systemds/src/test/scripts/functions/transform/input/20news_untokenized/20news-18828/sci.crypt")
dia.eachFile {
    print(it.getName())
    println(it)
    final Session session = Session.getDefaultInstance(new Properties());
    final MimeMessage message = MimeMessageUtils.createMimeMessage(session, it);
    final MimeMessageParser mimeMessageParser = new MimeMessageParser(message);
    mimeMessageParser.parse();
    println mimeMessageParser.getSubject()

    print("----------------------------------\n")

    // feed in your array (or convert your data to an array)
    String[] entries = [it.getName(), mimeMessageParser.getPlainContent()]

    writer.writeNext(entries);
}

writer.close();

