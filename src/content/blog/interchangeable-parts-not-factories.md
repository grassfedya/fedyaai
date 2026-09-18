---
title: Interchangeable parts, not factories
description: "Buidl interchangeable software parts not software factories. "
date: 2026-09-17
updated: 2026-09-17
draft: false
---
### You

You've been developing with AI for over a year now. You were probably one of the first adopters of claude code and remember that first feeling of "holy shit" when you used opus 4.6. You have probably worked on more projects than you ever have, utilizing tmux, remote sessions, and even extra machines to run more sessions.  You have probably seen everyone on X posting about how much money they are making and how fast they are moving so you naturally thought "I need to go faster."  And rather than dedicating more time to the current project you are working on, you instead decide to build something that will build that project for you: The software factory.  

### Software factories in a nutshell

*"Im going to spend 2 weeks building a thing that will build the thing that would take me 2 days to build!"*

![image.png](/images/image-6.png)

Have you built a software factory with the naive goals of being able to feed it an intent and then have it churn out the finished products but when you put it in practice you end up spending more time working on getting the tooling to work rather than actually building? So you eventually get tired of firing off long running loops which create heaps of work and make you feel like an alien in your own codebase and finally resort back to vanilla prompting to build features? If yes, welcome to the club. 

If you have followed leaders in the ai adoption space like the father of the ralph loop [Mr. Huntley](https://ghuntley.com/) and the tyrant of Gas Town [Mr. Yegge](https://yegge.ai/) then you know that they have tried multiple times to build the software factories of the future. Geoffrey with Loom, Steve with Gas Town and now Wheelhouse. It seems that all of these attempts have ended in the same spot: the code to support the factory grows so large and bureaucratic that you end up spending more time building the factory than the factory does building your product. And the time spent by the factory actually performing its intended purpose is overshadowed by the overwhelming amount of token spend for underwhelming results. 

This is not to say these projects are failures or even wastes of time. In fact they are huge successes for the community as they have shown us the limitations of ai without us having to spend [12k a month on subscription plans.](https://yegge.ai/essays/seats-and-sunsets/) Something that is top of mind for me when building is what Geoffrey said: "Agents are drunk." If you take this approach for your ai development you will have much greater successes. And the proof is in the pudding, let a loop run without extremely fixed constraints or a down-to-the-last-letter-specific goal then you will wake up to, well for a lack of better words: shit. 

![image.png](blob:https:/app.pagescms.org/4d6a2167-7c7c-48f1-a252-4a4b661a9e99)

###   
Software factories are bad generalists

We are looking at software factories all wrong. We are trying to build factories that will build us anything, however this is not how factories work. Historically factories have always been specialized. Theres no factory that builds gears for transmission boxes, glass for windowpanes, and toys. Instead there are gear factories, glass factories, and toy factories. Each one is specialized to producing one specific output from the same inputs. **So how can we apply that to software?**  How do we avoid waking up to extra brown brownfield projects every time we run our factories? Well what if instead of focusing on building factories, we focus on building interchangeable parts.

### Interchangeable parts

Session management, security, payment, user management, and hosting. These are almost always in every single application (im sure you can find tons more). So what if instead of having our agents build them from scratch every time on a new project we build each one once and then just reuse it. And then you consume those interchangeable parts and then add in custom application specific logic. I think pre-ai code is going to become our saving grace. The agents **are** drunk. And they hate taking things away and love adding them. If you tell them to improve an already perfect auth function they will find something and add either a comment or a different function call somewhere. So how about we just build the perfect auth function and tell them to wire it up to whatever latest project we are working on. I think n8n started with something like this but they missed the mark because no one likes node based languages. But that is kinda what I am proposing. I mean really, how much unique logic does any given application have. Most of the code to start with is the boilerplate that I mentioned at the start of this paragraph. If you have that handled in a plug and play fashion that gives you more time and bandwidth to handle the important stuff. 

### The "Monadrepo"

I am purely speculating here but an architecture I have been playing around with in my mind is the "monadrepo." Basically the monorepo of monorepos. You would have a reusable functions layer (the boilerplate) that your sub monorepos can pull from. That way if there are fixes to be made you fix them in one spot rather than 30. Basically copying the architecture of frontend libraries like shadcn or materialui but for fullstack components. You should be able to say "use e2e/auth.pkg for auth in my new mobile app" and it plugs it in and your signup, login, and auth related flows work out of the box. You might be thinking "ok but this would go from being project specific to person / team specific" and you are right! That is the point. Code quality is subjective. and the standards of one organization are vastly different than others. The point of interchangeable parts is not to standardize across the entire world, but within your organization first. Maybe in a couple months when the next frontier model comes out and the agi hype whistleblowers go on their tour again we can revisit this conversation and you can say "you are such a idiot software factories are possible now." But I don't think we will get there within the next 2 years at least. 