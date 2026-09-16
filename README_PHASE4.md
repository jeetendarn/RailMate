# RailMate Phase 4

This package adds the railway-data-provider abstraction.

Architecture:

User
  -> RailMate AI
  -> Python controller
  -> RailwayDataProvider
       -> DemoRailwayProvider
       -> LiveRailwayProvider (future authorized API)
  -> deterministic recommendation
  -> user review
  -> official railway booking service

The current live provider intentionally does not contain guessed endpoints.

This is deliberate: RailMate should connect only to an authorized railway information/e-ticketing service whose API contract has been obtained and verified.
