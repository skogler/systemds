@GrabConfig(systemClassLoader = true)
@Grab(group = "org.apache.commons", module = "commons-email", version = "1.5")
@Grab(group = "com.opencsv", module = "opencsv", version = "5.3")

import org.apache.commons.mail.util.*
import javax.mail.Session
import javax.mail.internet.MimeMessage
import com.opencsv.CSVWriter

CSVWriter writer = new CSVWriter(new FileWriter(args[1]));
dia = new File(args[0])
if (!dia.isDirectory()) {
    println "ERROR: Given file path ${args[0]} is not a directory!"
    System.exit(1)
}
println "Reading newsgroup files from ${args[0]}"
numRows = 0
dia.eachFile {
    final Session session = Session.getDefaultInstance(new Properties());
    final MimeMessage message = MimeMessageUtils.createMimeMessage(session, it);
    final MimeMessageParser mimeMessageParser = new MimeMessageParser(message);
    mimeMessageParser.parse();
    String[] entries = [it.getName(), mimeMessageParser.getPlainContent()]
    writer.writeNext(entries);
    numRows += 1
}
writer.close();
println "Wrote ${numRows} rows to ${args[1]}"

