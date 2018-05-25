from django.db import models


class Investments(models.Model):

    """Model representing each investment made by users"""

    investmentID = models.IntegerField(primary_key=True)

    number_shares = models.IntegerField(help_text="Number of shares bought or \
                                        sold in this transaction",
                                        verbose_name="Number of Shares")

    transaction_date = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of transaction",
                                            verbose_name="Transaction Date")

    transaction_type = models.IntegerField(choices=((-1, "Sell"), (1, "Buy")),
                                           help_text="Show whether transaction\
                                           was a buy or sell",
                                           verbose_name="Transaction Type")

    transaction_mode = models.IntegerField(choices=((-1, "User Generated"),
                                                    (1,
                                                     "Automatically Generated")))

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.).
        """
        return self.investmentID
