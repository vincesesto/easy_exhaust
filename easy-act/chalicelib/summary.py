import random

summaries = [
         "I have been working hard this week and have been getting through a lot of my training. Even though the training has been tough, I am greatful to be able to get out there as not everyone has the same luxuary that I do",
         "This week has been a pretty tough week. I have been training hard and trying my best to get through all my training. I keep telling myself that getting through these tough weeks take resiliance and will make me stronger at the end of the day.",
         "It's been another crazy week and I am not sure if I am busy or just doing lots of training. Needless to say, I love being able to do something that I an enjoy and hope that my training is moving in the right direction.",
         "I hope my weekly summaries don't sound like mindless cliches. But I honestly love getting through each of my training sessions. I just take it \"day by day\", \"week by week\", \"cliche by cliche\" ;) ."]

def random_summary():
    return random.choice(summaries)
