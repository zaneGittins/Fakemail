using System;
using System.Net.Mail;

namespace Mailer
{
    class Program
    {
        static string email_address = "test@evilcorp.com";
        static string email_password = "password";
        static string email_subject = "subject";
        static string email_body = "email for evilcorp.com";
        static string destination_address = "wellick@evilcorp.com";

        static void Main(string[] args)
        {
            SmtpClient smtpClient = new SmtpClient(args[0], int.Parse(args[1]));

            smtpClient.Credentials = new System.Net.NetworkCredential(email_address, email_password);
            smtpClient.DeliveryMethod = SmtpDeliveryMethod.Network;
            smtpClient.EnableSsl = false;
            MailMessage mail = new MailMessage();

            mail.From = new MailAddress(email_address);
            mail.Subject = email_subject;
            mail.To.Add(new MailAddress(destination_address));
            mail.Body = email_body;

            smtpClient.Send(mail);

            Console.WriteLine("[+] Sent email from " + email_address + " to " + destination_address);
        }
    }
}
