                 USER
                   │
                   ▼
             POST /predict
                   │
                   ▼
              Middleware
                   │
                   ▼
              ML Model
                   │
                   ▼
          Disease + Confidence
                   │
                   ▼
             Metrics Store
                   │
          ┌────────┴────────┐
          ▼                 ▼
      /metrics          Monitoring
                            │
                            ▼
                    Drift Detection
                       /          \
                      ▼            ▼
                  Training      New Data